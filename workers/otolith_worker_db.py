import pika
import json
import os
import time
import base64
import cv2
import numpy as np
import psycopg2

# --- Database Configuration ---
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

db_connection = None

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def process_message(ch, method, properties, body):
    """Callback function to process an otolith image and save results to the DB."""
    message = json.loads(body)
    image_data_b64 = message.get("image_data")
    image_id = message.get("image_id", f"unknown-{int(time.time())}")

    if not image_data_b64:
        print(f" [!] Message for {image_id} has no image data. Skipping.")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    print(f" [x] Received otolith image: {image_id}. Starting analysis...")

    try:
        # --- OpenCV Processing (same as before) ---
        image_bytes = base64.b64decode(image_data_b64)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode image.")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            print(f"  - No contours found for {image_id}.")
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
        print(f"  - Analysis Complete. Results: {results}")

        # --- SAVE RESULTS TO DATABASE ---
        global db_connection
        if not db_connection or db_connection.closed:
            print("  - Re-establishing DB connection...")
            db_connection = get_db_connection()

        with db_connection.cursor() as cur:
            # Use INSERT with ON CONFLICT to handle re-analysis of the same image
            cur.execute("""
                INSERT INTO otolith_morphometrics (image_id, area_px, perimeter_px, width_px, height_px, aspect_ratio)
                VALUES (%(image_id)s, %(area_px)s, %(perimeter_px)s, %(width_px)s, %(height_px)s, %(aspect_ratio)s)
                ON CONFLICT (image_id) DO UPDATE SET
                    area_px = EXCLUDED.area_px,
                    perimeter_px = EXCLUDED.perimeter_px,
                    width_px = EXCLUDED.width_px,
                    height_px = EXCLUDED.height_px,
                    aspect_ratio = EXCLUDED.aspect_ratio,
                    analysis_timestamp = CURRENT_TIMESTAMP;
            """, results)
            db_connection.commit()
            print(f"  - Successfully saved results for {image_id} to the database.")

    except Exception as e:
        print(f" [!] Error processing image {image_id}: {e}")
        # In a production system, you might requeue the message or move it to a dead-letter queue
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f" [x] Done. Acknowledged message for {image_id}.")


def main():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    connection = None
    retries = 10
    while retries > 0:
        try:
            print(" [*] Otolith Worker (DB): Attempting to connect to RabbitMQ...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            print(" [*] Otolith Worker (DB): RabbitMQ connection successful.")
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"Connection to RabbitMQ failed. Retrying in 5 seconds...")
            retries -= 1
            time.sleep(5)

    if not connection:
        print(" [!] Could not connect to RabbitMQ. Exiting.")
        return

    # Establish initial DB connection
    global db_connection
    try:
        db_connection = get_db_connection()
        print(" [*] Otolith Worker (DB): Database connection successful.")
    except psycopg2.OperationalError as e:
        print(f" [!] CRITICAL: Could not connect to database on startup: {e}")
        return

    channel = connection.channel()
    channel.queue_declare(queue='otolith_queue', durable=True)
    print(' [*] Otolith Worker (DB): Waiting for messages. To exit press CTRL+C')
    channel.basic_consume(queue='otolith_queue', on_message_callback=process_message)
    channel.start_consuming()

if __name__ == '__main__':
    main()
