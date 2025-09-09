import pika
import json
import os
import time
import base64
import cv2
import numpy as np
import psycopg2

# DB Config is the same as otolith_worker_db.py
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "cmlre_data")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

db_connection = None

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)

def process_message(ch, method, properties, body):
    message = json.loads(body)
    image_data_b64 = message.get("image_data")
    image_id = message.get("image_id", f"unknown-{int(time.time())}")
    
    # ... (OpenCV processing logic is identical to otolith_worker_db.py) ...
    try:
        image_bytes = base64.b64decode(image_data_b64)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None: raise ValueError("Could not decode image.")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        main_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(main_contour)
        perimeter = cv2.arcLength(main_contour, True)
        _, _, w, h = cv2.boundingRect(main_contour)
        aspect_ratio = round(w / h if h > 0 else 0, 3)

        results = {
            "image_id": image_id,
            "area_px": float(area),
            "perimeter_px": round(float(perimeter), 2),
            "width_px": int(w),
            "height_px": int(h),
            "aspect_ratio": float(aspect_ratio)
        }
        
        global db_connection
        if not db_connection or db_connection.closed:
            db_connection = get_db_connection()

        with db_connection.cursor() as cur:
            cur.execute("""
                INSERT INTO otolith_morphometrics (image_id, area_px, perimeter_px, width_px, height_px, aspect_ratio)
                VALUES (%(image_id)s, %(area_px)s, %(perimeter_px)s, %(width_px)s, %(height_px)s, %(aspect_ratio)s)
                ON CONFLICT (image_id) DO UPDATE SET
                    area_px = EXCLUDED.area_px, perimeter_px = EXCLUDED.perimeter_px,
                    width_px = EXCLUDED.width_px, height_px = EXCLUDED.height_px,
                    aspect_ratio = EXCLUDED.aspect_ratio, analysis_timestamp = CURRENT_TIMESTAMP;
            """, results)
            db_connection.commit()
            print(f"  - Saved morphometrics for {image_id} to the database.")

        # --- NEW: TRIGGER AI WORKER ---
        # After saving, publish the results to the AI queue for prediction
        ch.queue_declare(queue='ai_queue', durable=True)
        ch.basic_publish(
            exchange='',
            routing_key='ai_queue',
            body=json.dumps(results),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"  - Sent results for {image_id} to AI queue for prediction.")

    except Exception as e:
        print(f" [!] Error processing image {image_id}: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    # ... (Main connection logic is identical to otolith_worker_db.py) ...
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    global db_connection
    db_connection = get_db_connection()
    channel = connection.channel()
    channel.queue_declare(queue='otolith_queue', durable=True)
    channel.basic_consume(queue='otolith_queue', on_message_callback=process_message)
    channel.start_consuming()

if __name__ == '__main__':
    main()
