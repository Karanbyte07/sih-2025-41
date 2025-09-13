#!/usr/bin/env python3
import pika
import json
import time
import sys

def simple_worker():
    """A simple test worker to verify message consumption"""
    print("🔄 Starting simple test worker...")
    
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    
    # Declare queue
    channel.queue_declare(queue='otolith_queue', durable=True)
    
    def callback(ch, method, properties, body):
        print(f"📩 RECEIVED MESSAGE: {body}")
        try:
            data = json.loads(body)
            print(f"✅ Parsed data: {data}")
            print(f"📋 Image ID: {data.get('image_id', 'Unknown')}")
            print(f"📊 Image data length: {len(data.get('image_data', ''))}")
        except Exception as e:
            print(f"❌ Error parsing message: {e}")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("✅ Message acknowledged")
        print("-" * 50)
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='otolith_queue', on_message_callback=callback)
    
    print("👂 Waiting for messages. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("🛑 Stopping worker...")
        channel.stop_consuming()
        connection.close()

if __name__ == '__main__':
    simple_worker()