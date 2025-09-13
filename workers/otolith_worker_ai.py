import pika
import json
import base64
import cv2
import numpy as np
import time
import os
import sys
from sqlalchemy import create_engine, text
from PIL import Image
import io
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- Configuration ---
RABBITMQ_HOST = 'rabbitmq'
DATABASE_URL = "postgresql://postgres:postgres@db:5432/cmlre_data"

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

def validate_image_data(image_data):
    """Validate image data before processing."""
    try:
        # Try to decode with PIL first to catch PNG corruption issues
        image = Image.open(io.BytesIO(image_data))
        image.verify()  # This will raise an exception if the image is corrupted
        return True
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False

def process_message(ch, method, properties, body):
    """Callback function to process a message from the queue."""
    logger.info(f"Received message: {body}")
    try:
        data = json.loads(body)
        image_id = data['image_id']
        image_data = base64.b64decode(data['image_data'])
        
        logger.info(f"Processing image: {image_id}")

        # Validate image data before processing
        if not validate_image_data(image_data):
            logger.warning(f"Skipping corrupted image {image_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # --- OpenCV Processing ---
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
        
        # Check if image was successfully decoded
        if img is None:
            logger.error(f"Failed to decode image {image_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            main_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(main_contour)
            perimeter = cv2.arcLength(main_contour, True)
            x, y, w, h = cv2.boundingRect(main_contour)
            aspect_ratio = float(w) / h if h != 0 else 0
            
            metrics = {
                "image_id": image_id,
                "area": area,
                "perimeter": perimeter,
                "width": w,
                "height": h,
                "aspect_ratio": aspect_ratio
            }
            logger.info(f"Calculated metrics for {image_id}: {metrics}")

            # --- Save to Database ---
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                insert_sql = text("""
                    INSERT INTO otolith_morphometrics (image_id, area, perimeter, width, height, aspect_ratio, latitude, longitude)
                    VALUES (:image_id, :area, :perimeter, :width, :height, :aspect_ratio, :lat, :lon)
                    ON CONFLICT (image_id) DO UPDATE SET
                        area = EXCLUDED.area,
                        perimeter = EXCLUDED.perimeter,
                        width = EXCLUDED.width,
                        height = EXCLUDED.height,
                        aspect_ratio = EXCLUDED.aspect_ratio,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude;
                """)
                # Add mock location data
                params = {**metrics, "lat": 15.5 - (area % 1000) / 5000, "lon": -75.2 - (perimeter % 1000) / 5000}
                conn.execute(insert_sql, params)
                conn.commit()
            logger.info(f"Saved metrics for {image_id} to database.")

            # --- Trigger AI Worker ---
            channel = ch.connection.channel()
            channel.queue_declare(queue='ai_queue', durable=True)
            ai_message = json.dumps(metrics)
            channel.basic_publish(
                exchange='',
                routing_key='ai_queue',
                body=ai_message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            logger.info(f"Sent metrics for {image_id} to AI queue.")

    except Exception as e:
        logger.error(f"Error processing message: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    """Main function to start the otolith worker with connection recovery."""
    logger.info("Starting main function...")
    while True:
        try:
            logger.info("Attempting to connect to RabbitMQ...")
            connection = connect_to_rabbitmq()
            logger.info("Creating channel...")
            channel = connection.channel()
            logger.info("Declaring queue...")
            channel.queue_declare(queue='otolith_queue', durable=True)
            
            logger.info("Setting QoS...")
            channel.basic_qos(prefetch_count=1)
            logger.info("Setting up consumer...")
            channel.basic_consume(queue='otolith_queue', on_message_callback=process_message)
            
            logger.info('Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()
            
        except pika.exceptions.StreamLostError as e:
            logger.error(f"Lost connection to RabbitMQ ({e}). Reconnecting in 5 seconds...")
            time.sleep(5)
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"AMQP Connection error ({e}). Reconnecting in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            logger.info('Interrupted by user')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except Exception as e:
            logger.error(f"Unexpected error: {e}. Reconnecting in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    logger.info("Script started")
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
