import pika
import json
import time

def send_test_message():
    """Send a test message directly to the queue"""
    
    # Test message
    test_message = {
        "image_id": f"direct-test-{int(time.time())}",
        "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGhxI7nYwAAAABJRU5ErkJggg=="
    }
    
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        
        # Declare queue
        channel.queue_declare(queue='otolith_queue', durable=True)
        
        # Send message
        message_body = json.dumps(test_message)
        channel.basic_publish(
            exchange='',
            routing_key='otolith_queue',
            body=message_body,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        print(f"✅ Sent test message: {test_message['image_id']}")
        connection.close()
        
        return test_message['image_id']
        
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        return None

if __name__ == "__main__":
    print("Sending direct test message to RabbitMQ...")
    message_id = send_test_message()
    
    if message_id:
        print(f"Message sent with ID: {message_id}")
        print("Check worker logs and database in a few seconds...")