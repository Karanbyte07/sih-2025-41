import pika
import json
import os
import time
import pickle
import pandas as pd
import psycopg2

# --- Database Configuration ---
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "cmlre_data")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# --- Model Loading ---
MODEL_PATH = "/app/model/species_classifier.pkl"
classifier = None

def load_model():
    """Loads the pre-trained classifier model from disk."""
    global classifier
    retries = 10
    while retries > 0:
        try:
            with open(MODEL_PATH, 'rb') as f:
                classifier = pickle.load(f)
            print(" [x] AI Model loaded successfully.")
            return
        except FileNotFoundError:
            print(f" [!] Model file not found at {MODEL_PATH}. Retrying in 5 seconds...")
            time.sleep(5)
            retries -= 1
    raise Exception("Could not load AI model. Shutting down.")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)

def process_message(ch, method, properties, body):
    """Callback to process a message, run prediction, and update DB."""
    data = json.loads(body)
    image_id = data.get("image_id", "unknown")
    print(f" [x] Received request for AI prediction for image: {image_id}")

    if not classifier:
        print(" [!] Classifier model is not loaded. Cannot process message.")
        # Negative acknowledgement to requeue the message
        ch.basic_nack(delivery_tag=method.delivery_tag)
        return

    try:
        # 1. Prepare data for prediction
        features = pd.DataFrame([data])
        # Ensure columns are in the same order as during training
        features = features[['area_px', 'perimeter_px', 'width_px', 'height_px', 'aspect_ratio']]
        
        # 2. Make prediction
        prediction = classifier.predict(features)[0]
        print(f"  - AI Prediction for {image_id}: {prediction}")

        # 3. Save prediction back to the database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Add a new column if it doesn't exist and update the record
                cur.execute("ALTER TABLE otolith_morphometrics ADD COLUMN IF NOT EXISTS predicted_species VARCHAR(255);")
                cur.execute(
                    "UPDATE otolith_morphometrics SET predicted_species = %s WHERE image_id = %s;",
                    (prediction, image_id)
                )
                conn.commit()
                print(f"  - Saved prediction to database for {image_id}.")

    except Exception as e:
        print(f" [!] Error during AI prediction for {image_id}: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f" [x] Acknowledged message for {image_id}.")


def main():
    load_model() # Load model on startup

    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue='ai_queue', durable=True)
    print(' [*] AI Worker: Waiting for messages. To exit press CTRL+C')
    channel.basic_consume(queue='ai_queue', on_message_callback=process_message)
    channel.start_consuming()

if __name__ == '__main__':
    main()
