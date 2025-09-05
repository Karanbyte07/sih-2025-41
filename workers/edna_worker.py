import pika
import json
import os
import time

def process_message(ch, method, properties, body):
    """Callback function to process a message from the queue."""
    data = json.loads(body)
    print(f" [x] Received eDNA data: {data}")

    # --- MOCK PROCESSING ---
    # In a real application, you would use Biopython here to:
    # 1. Fetch the sequence data for `data['sequence_id']`.
    # 2. Run BLAST searches, sequence alignments, or other genetic analyses.
    # 3. Store the findings in the database.
    print("  - Simulating genetic analysis with Biopython...")
    time.sleep(4) # Simulate a long-running task
    print(f"  - Analysis complete for {data['sequence_id']}.")
    # --- END MOCK ---

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(" [x] Done")

def main():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    connection = None

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
    channel.queue_declare(queue='edna_queue', durable=True)
    print(' [*] eDNA Worker: Waiting for messages. To exit press CTRL+C')
    channel.basic_consume(queue='edna_queue', on_message_callback=process_message)
    channel.start_consuming()

if __name__ == '__main__':
    main()

