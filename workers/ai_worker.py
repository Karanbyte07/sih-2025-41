import pika
import json
import time
import os
import joblib
import pandas as pd
from sqlalchemy import create_engine, text
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
RABBITMQ_HOST = 'rabbitmq'
DATABASE_URL = "postgresql://postgres:postgres@db:5432/cmlre_data"
MODEL_PATH = "/app/ai_model/species_classifier.pkl"
AI_QUEUE = 'ai_queue'

# Global variable to hold the model
model = None

def load_model():
    """Load the trained model from disk with a retry mechanism."""
    global model
    max_retries = 12
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        if os.path.exists(MODEL_PATH):
            logger.info(f"Loading model from {MODEL_PATH}")
            model = joblib.load(MODEL_PATH)
            logger.info("Model loaded successfully.")
            return
        else:
            logger.warning(f"Model file not found at {MODEL_PATH}. Retrying in {retry_delay} seconds... ({attempt + 1}/{max_retries})")
            time.sleep(retry_delay)

    raise Exception("Could not load AI model after multiple retries. Shutting down.")

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

def predict_species(data):
    """Predicts species based on morphometric data."""
    if model is None:
        logger.error("Model is not loaded. Cannot predict.")
        return "Error: Model not loaded"
    try:
        df = pd.DataFrame([data])
        df = df[['area', 'perimeter', 'width', 'height', 'aspect_ratio']]
        prediction = model.predict(df)
        logger.info(f"Prediction made: {prediction[0]}")
        return prediction[0]
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        return "Error: Prediction failed"

def update_prediction_in_db(image_id, species):
    """Updates the database record with the predicted species."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            stmt = text("UPDATE otolith_morphometrics SET predicted_species = :species WHERE image_id = :image_id;")
            conn.execute(stmt, {'species': species, 'image_id': image_id})
            conn.commit()
            logger.info(f"Updated DB for {image_id} with prediction: {species}")
    except Exception as e:
        logger.error(f"Database update failed for {image_id}: {e}")

def callback(ch, method, properties, body):
    """Callback function to process messages from the queue."""
    logger.info(f"Received message: {body}")
    try:
        data = json.loads(body)
        image_id = data.get('image_id')
        if not image_id:
            logger.warning("Received message without image_id.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
            
        logger.info(f"Processing data for {image_id}")
        predicted_species = predict_species(data)
        if "Error" not in predicted_species:
            update_prediction_in_db(image_id, predicted_species)
    except Exception as e:
        logger.error(f"Exception in callback: {e}")
    finally:
        try:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as ack_err:
            logger.error(f"Failed to ack message: {ack_err}")

def main():
    """Main function to start the AI worker."""
    logger.info("Starting AI worker...")
    load_model()
    while True:
        try:
            connection = connect_to_rabbitmq()
            channel = connection.channel()
            channel.queue_declare(queue=AI_QUEUE, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=AI_QUEUE, on_message_callback=callback)
            logger.info('Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()
        except pika.exceptions.StreamLostError as e:
            logger.error(f"Lost connection to RabbitMQ ({e}). Reconnecting in 5 seconds...")
            time.sleep(5)
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"AMQP Connection error ({e}). Reconnecting in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            logger.info('Interrupted')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except Exception as e:
            logger.error(f"Unexpected error: {e}. Reconnecting in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    logger.info("AI Worker script started")
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

