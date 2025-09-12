import pika
import json
import base64
import cv2
import numpy as np
import time
import os
from sqlalchemy import create_engine, text

# --- Configuration ---
RABBITMQ_HOST = 'rabbitmq'
DATABASE_URL = "postgresql://postgres:postgres@db:5432/cmlre_data"

def connect_to_rabbitmq():
    """Connect to RabbitMQ with a retry mechanism."""
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            print("[*] Otolith Worker: Successfully connected to RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("[!] Otolith Worker: RabbitMQ not ready. Retrying in 5 seconds...")
            time.sleep(5)

def process_message(ch, method, properties, body):
    """Callback function to process a message from the queue."""
    try:
        data = json.loads(body)
        image_id = data['image_id']
        image_data = base64.b64decode(data['image_data'])
        
        print(f"[*] Otolith Worker: Received image {image_id}")

        # --- OpenCV Processing ---
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
        
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
            print(f"[*] Otolith Worker: Calculated metrics for {image_id}: {metrics}")

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
            print(f"[*] Otolith Worker: Saved metrics for {image_id} to database.")

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
            print(f"[*] Otolith Worker: Sent metrics for {image_id} to AI queue.")

    except Exception as e:
        print(f"[!] Otolith Worker: Error processing message: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue='otolith_queue', durable=True)
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='otolith_queue', on_message_callback=process_message)
    
    print('[*] Otolith Worker: Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()
