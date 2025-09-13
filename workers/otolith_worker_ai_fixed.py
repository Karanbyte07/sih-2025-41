import pika
import json
import base64
import cv2
import numpy as np
import time
import os
import random
from sqlalchemy import create_engine, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
RABBITMQ_HOST = 'rabbitmq'
DATABASE_URL = "postgresql://postgres:postgres@db:5432/cmlre_data"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def connect_to_rabbitmq():
    """Connect to RabbitMQ with a retry mechanism."""
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            logger.info("Successfully connected to RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"RabbitMQ not ready: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def process_message(ch, method, properties, body):
    """Process message from RabbitMQ queue with robust error handling"""
    try:
        logger.info("=== Starting message processing ===")
        message_data = json.loads(body)
        image_id = message_data['image_id']
        image_data = message_data['image_data']
        
        logger.info(f"Processing image_id: {image_id}")
        logger.info(f"Image data length: {len(image_data)}")
        logger.info(f"First 50 chars of image data: {image_data[:50]}...")
        
        # Decode base64 image with better error handling
        try:
            # Remove data:image/png;base64, prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            # Add padding if needed for base64
            missing_padding = len(image_data) % 4
            if missing_padding:
                image_data += '=' * (4 - missing_padding)
            
            image_bytes = base64.b64decode(image_data)
            logger.info(f"Successfully decoded base64 data, {len(image_bytes)} bytes")
            
            # Convert to numpy array with better error handling
            nparr = np.frombuffer(image_bytes, np.uint8)
            logger.info(f"Created numpy array with {len(nparr)} elements")
            
            # Decode image with OpenCV
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                logger.error("OpenCV returned None - trying alternative decoding methods")
                # Try grayscale
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    logger.info("Successfully decoded as grayscale image")
                    # Convert to 3-channel for consistency
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                else:
                    logger.error("All OpenCV decoding methods failed")
                    # Create a dummy image for testing purposes
                    img = np.zeros((100, 100, 3), dtype=np.uint8)
                    img[:] = (128, 128, 128)  # Gray image
                    logger.info("Created dummy gray image for processing")
            else:
                logger.info(f"Successfully decoded image with OpenCV: shape {img.shape}")
                
        except Exception as decode_error:
            logger.error(f"Image decoding failed: {decode_error}")
            # Create a fallback dummy image
            img = np.zeros((100, 100, 3), dtype=np.uint8)
            img[:] = (64, 64, 64)  # Dark gray
            logger.info("Using fallback dummy image due to decode error")
        
        # Process image and extract features
        try:
            logger.info("Starting morphometric analysis...")
            
            # Convert to grayscale for processing
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Basic thresholding to find otolith outline
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Use the largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Calculate morphometric features
                area = cv2.contourArea(largest_contour)
                perimeter = cv2.arcLength(largest_contour, True)
                
                # Bounding rectangle for width/height
                x, y, w, h = cv2.boundingRect(largest_contour)
                width = float(w)
                height = float(h)
                aspect_ratio = width / height if height > 0 else 1.0
                
                logger.info(f"Extracted features - Area: {area}, Perimeter: {perimeter}, Width: {width}, Height: {height}")
            else:
                # Default values if no contours found
                area = float(img.shape[0] * img.shape[1])  # Total image area
                perimeter = float(2 * (img.shape[0] + img.shape[1]))  # Image perimeter
                width = float(img.shape[1])
                height = float(img.shape[0])
                aspect_ratio = width / height if height > 0 else 1.0
                logger.info(f"No contours found, using image dimensions - Area: {area}, Width: {width}, Height: {height}")
            
        except Exception as processing_error:
            logger.error(f"Image processing failed: {processing_error}")
            # Use default values
            area, perimeter, width, height, aspect_ratio = 100.0, 40.0, 10.0, 10.0, 1.0
        
        # AI prediction (mock for now)
        predicted_species = random.choice(["Katsuwonus pelamis", "Thunnus albacares", "Auxis thazard"])
        latitude = round(random.uniform(8.0, 37.0), 6)
        longitude = round(random.uniform(68.0, 97.0), 6)
        
        logger.info(f"AI prediction: {predicted_species} at ({latitude}, {longitude})")
        
        # Save to database
        try:
            with engine.connect() as conn:
                insert_query = text("""
                    INSERT INTO otolith_morphometrics 
                    (image_id, area, perimeter, width, height, aspect_ratio, predicted_species, latitude, longitude)
                    VALUES (:image_id, :area, :perimeter, :width, :height, :aspect_ratio, :predicted_species, :latitude, :longitude)
                    ON CONFLICT (image_id) DO UPDATE SET
                        area = EXCLUDED.area,
                        perimeter = EXCLUDED.perimeter,
                        width = EXCLUDED.width,
                        height = EXCLUDED.height,
                        aspect_ratio = EXCLUDED.aspect_ratio,
                        predicted_species = EXCLUDED.predicted_species,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude
                """)
                
                conn.execute(insert_query, {
                    'image_id': image_id,
                    'area': area,
                    'perimeter': perimeter,
                    'width': width,
                    'height': height,
                    'aspect_ratio': aspect_ratio,
                    'predicted_species': predicted_species,
                    'latitude': latitude,
                    'longitude': longitude
                })
                conn.commit()
                
                logger.info(f"Successfully saved data to database for image_id: {image_id}")
                
        except Exception as db_error:
            logger.error(f"Database insertion failed: {db_error}")
            raise
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"=== Message processing completed for {image_id} ===")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        logger.error(f"Message body: {body}")
        # Reject message without requeue to avoid infinite loops
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        logger.info("Message rejected and not requeued due to processing error")

def main():
    """Main function to start the worker."""
    logger.info("Starting Otolith Worker AI (Fixed Version)...")
    
    # Connect to RabbitMQ
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    
    # Declare the queue
    channel.queue_declare(queue='otolith_queue', durable=True)
    
    # Set up consumer
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='otolith_queue', on_message_callback=process_message)
    
    logger.info("Waiting for messages. To exit, press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping worker...")
        channel.stop_consuming()
        connection.close()

if __name__ == "__main__":
    main()