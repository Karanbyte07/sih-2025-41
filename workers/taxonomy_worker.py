import pika
import json
import os
import time
import sqlalchemy
from sqlalchemy.orm import sessionmaker

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/mydatabase")

# Define the table structure to match the one in main.py
metadata = sqlalchemy.MetaData()
taxonomies = sqlalchemy.Table(
    "taxonomies",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, unique=True, index=True),
    sqlalchemy.Column("classification", sqlalchemy.String),
)
engine = sqlalchemy.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def process_message(ch, method, properties, body):
    """Callback function to process a message from the queue."""
    data = json.loads(body)
    print(f" [x] Received taxonomy data: {data}")

    db = SessionLocal()
    try:
        # Check if the taxonomy already exists
        existing = db.execute(taxonomies.select().where(taxonomies.c.name == data['name'])).first()
        if existing:
            print(f"  - Taxonomy '{data['name']}' already exists. Skipping.")
        else:
            # Insert new taxonomy data into the database
            ins = taxonomies.insert().values(name=data['name'], classification=data['classification'])
            db.execute(ins)
            db.commit()
            print(f"  - Successfully saved '{data['name']}' to the database.")
    except Exception as e:
        print(f"  - Error processing message: {e}")
        db.rollback()
    finally:
        db.close()

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(" [x] Done")

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
    channel.queue_declare(queue='taxonomy_queue', durable=True)
    print(' [*] Taxonomy Worker: Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='taxonomy_queue', on_message_callback=process_message)
    channel.start_consuming()

if __name__ == '__main__':
    main()
