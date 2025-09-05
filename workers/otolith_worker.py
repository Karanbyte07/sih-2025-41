import pika
import json
import os
import time
import base64
import cv2
import numpy as np

def process_message(ch, method, properties, body):
    """Callback function to process an otolith image from the queue."""
    message = json.loads(body)
    image_data_b64 = message.get("image_data")

    if not image_data_b64:
        print(" [!] Received message without image data. Acknowledging and skipping.")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    print(" [x] Received otolith image data. Starting analysis...")

    try:
        # --- REAL PROCESSING with OpenCV ---
        # 1. Decode Base64 string to bytes, then to a NumPy array
        image_bytes = base64.b64decode(image_data_b64)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode image.")

        # 2. Convert to grayscale and apply a binary threshold
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

        # 3. Find contours (the outline of the shape)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # 4. Assume the largest contour is the otolith
            main_contour = max(contours, key=cv2.contourArea)

            # 5. Calculate morphometrics
            area = cv2.contourArea(main_contour)
            perimeter = cv2.arcLength(main_contour, True)
            x, y, w, h = cv2.boundingRect(main_contour)

            results = {
                "area_px": area,
                "perimeter_px": round(perimeter, 2),
                "width_px": w,
                "height_px": h,
                "aspect_ratio": round(w / h if h > 0 else 0, 3)
            }
            print(f"  - Analysis Complete. Results: {results}")
            # In a full implementation, you would save these 'results' to the PostgreSQL database
            # Example: db.save_otolith_metrics(sample_id, results)

        else:
            print("  - No contours found in the image.")

    except Exception as e:
        print(f" [!] Error processing image: {e}")

    # --- END REAL PROCESSING ---

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(" [x] Done. Acknowledged message.")


def main():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    connection = None
    # Retry connection to RabbitMQ
    for i in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"Connection to RabbitMQ failed. Retrying in {i+2} seconds...")
            time.sleep(i + 2)
    if not connection:
        print("Could not connect to RabbitMQ. Exiting.")
        return

    channel = connection.channel()
    channel.queue_declare(queue='otolith_queue', durable=True)
    print(' [*] Otolith Worker: Waiting for messages. To exit press CTRL+C')
    channel.basic_consume(queue='otolith_queue', on_message_callback=process_message)
    channel.start_consuming()

if __name__ == '__main__':
    main()

