#!/usr/bin/env python3
"""
Test script to debug message flow in the CMLRE system.
This script tests the complete pipeline from API to workers.
"""

import pika
import json
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
RABBITMQ_HOST = 'localhost'
API_BASE_URL = 'http://localhost:8000'

def test_rabbitmq_connection():
    """Test if we can connect to RabbitMQ."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        
        # Check queue status
        otolith_queue = channel.queue_declare(queue='otolith_queue', durable=True, passive=True)
        ai_queue = channel.queue_declare(queue='ai_queue', durable=True, passive=True)
        
        logger.info(f"RabbitMQ Connection: SUCCESS")
        logger.info(f"Otolith Queue: {otolith_queue.method.message_count} messages")
        logger.info(f"AI Queue: {ai_queue.method.message_count} messages")
        
        connection.close()
        return True
    except Exception as e:
        logger.error(f"RabbitMQ Connection: FAILED - {e}")
        return False

def test_api_endpoint():
    """Test if the API is responding."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/dashboard/data", timeout=5)
        logger.info(f"API Dashboard Endpoint: SUCCESS - Status {response.status_code}")
        logger.info(f"Response: {response.json()}")
        return True
    except Exception as e:
        logger.error(f"API Dashboard Endpoint: FAILED - {e}")
        return False

def test_otolith_ingest():
    """Test the otolith ingestion endpoint."""
    try:
        test_data = {
            "image_id": f"test-image-{int(time.time())}",
            "image_data": "iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAALiIAAC4iAari3ZIAAAHNSURBVHhe7dixTkJBFEbhD18gIgaJkUijaGRAZ4CiC4gkxcY0pC1JAY0tYAEH4ACwpCwJDRpERQNo2BgTNIFRg4kBMnlB4n/mB16a2Z35v9k3s59whQoVOrw+F9z6vD4XmF7fL37w5/VL32/d8TevP/d8wB/8+b43PK//nlv4l8y/P/91/s+L3/nwB7/56y/vl/6/BQD8v5sF+NkLAuBnbQiAn7UgAH7WggD4WQsC4GctCIDf/l386Pcr/28JAGB/LQgA/LwFAXBaswD4WQsC4GctCIDf/i0A4GctCICsLQGAf0gLAuBnbQiAn1UgAH7WggD4GgBgLQiA3/4d/ej3K/9vCQBgf1sQAPh5CgLgtGYB8LMWAuBnbQiA3/4tAMA+LQiArC0BgH9ICgLgZ20IgJ+1IChY/v0tAH7WggD4WQsC4GctCIB/SAYAYC0IgJ+1IAC+BgBYCwLgZy0IgJ+1IAC+BgB4v7YgAH7WggD4WQsC4GctCICsLQiAn7UgAH7WggD4WQsC4GctCICvtYEA+FkLAuBnbQiAn7UgAH7WggD4WQuB3/4d/ej3K/9vCQB4//oV+qV3gUKFCp0/rw+hTwA2H2qLRMdWbAAAAABJRU5ErkJggg=="
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/ingest/otolith",
            json=test_data,
            timeout=10
        )
        
        logger.info(f"API Otolith Ingest: SUCCESS - Status {response.status_code}")
        logger.info(f"Response: {response.json()}")
        return True
    except Exception as e:
        logger.error(f"API Otolith Ingest: FAILED - {e}")
        return False

def test_direct_rabbitmq_publish():
    """Test publishing directly to RabbitMQ."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='otolith_queue', durable=True)
        
        test_message = {
            "image_id": f"direct-test-{int(time.time())}",
            "image_data": "iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAALiIAAC4iAari3ZIAAAHNSURBVHhe7dixTkJBFEbhD18gIgaJkUijaGRAZ4CiC4gkxcY0pC1JAY0tYAEH4ACwpCwJDRpERQNo2BgTNIFRg4kBMnlB4n/mB16a2Z35v9k3s59whQoVOrw+F9z6vD4XmF7fL37w5/VL32/d8TevP/d8wB/8+b43PK//nlv4l8y/P/91/s+L3/nwB7/56y/vl/6/BQD8v5sF+NkLAuBnbQiAn7UgAH7WggD4WQsC4GctCIDf/l386Pcr/28JAGB/LQgA/LwFAXBaswD4WQsC4GctCIDf/i0A4GctCICsLQGAf0gLAuBnbQiAn1UgAH7WggD4GgBgLQiA3/4d/ej3K/9vCQBgf1sQAPh5CgLgtGYB8LMWAuBnbQiA3/4tAMA+LQiArC0BgH9ICgLgZ20IgJ+1IChY/v0tAH7WggD4WQsC4GctCIB/SAYAYC0IgJ+1IAC+BgBYCwLgZy0IgJ+1IAC+BgB4v7YgAH7WggD4WQsC4GctCICsLQiAn7UgAH7WggD4WQsC4GctCICvtYEA+FkLAuBnbQiAn7UgAH7WggD4WQuB3/4d/ej3K/9vCQB4//oV+qV3gUKFCp0/rw+hTwA2H2qLRMdWbAAAAABJRU5ErkJggg=="
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='otolith_queue',
            body=json.dumps(test_message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        logger.info("Direct RabbitMQ Publish: SUCCESS")
        connection.close()
        return True
    except Exception as e:
        logger.error(f"Direct RabbitMQ Publish: FAILED - {e}")
        return False

def monitor_queues():
    """Monitor queue status for 30 seconds."""
    logger.info("Monitoring queues for 30 seconds...")
    start_time = time.time()
    
    while time.time() - start_time < 30:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            
            otolith_queue = channel.queue_declare(queue='otolith_queue', durable=True, passive=True)
            ai_queue = channel.queue_declare(queue='ai_queue', durable=True, passive=True)
            
            logger.info(f"Queues - Otolith: {otolith_queue.method.message_count}, AI: {ai_queue.method.message_count}")
            
            connection.close()
            time.sleep(5)
        except Exception as e:
            logger.error(f"Queue monitoring error: {e}")
            time.sleep(5)

def main():
    """Run all tests."""
    logger.info("=== CMLRE Message Flow Test ===")
    
    # Test 1: RabbitMQ Connection
    logger.info("\n1. Testing RabbitMQ Connection...")
    rabbitmq_ok = test_rabbitmq_connection()
    
    # Test 2: API Dashboard
    logger.info("\n2. Testing API Dashboard...")
    api_ok = test_api_endpoint()
    
    # Test 3: API Otolith Ingest
    logger.info("\n3. Testing API Otolith Ingest...")
    ingest_ok = test_otolith_ingest()
    
    # Test 4: Direct RabbitMQ Publish
    logger.info("\n4. Testing Direct RabbitMQ Publish...")
    direct_ok = test_direct_rabbitmq_publish()
    
    # Test 5: Monitor Queues
    logger.info("\n5. Monitoring Queues...")
    monitor_queues()
    
    # Summary
    logger.info("\n=== TEST SUMMARY ===")
    logger.info(f"RabbitMQ Connection: {'PASS' if rabbitmq_ok else 'FAIL'}")
    logger.info(f"API Dashboard: {'PASS' if api_ok else 'FAIL'}")
    logger.info(f"API Otolith Ingest: {'PASS' if ingest_ok else 'FAIL'}")
    logger.info(f"Direct RabbitMQ Publish: {'PASS' if direct_ok else 'FAIL'}")
    
    if all([rabbitmq_ok, api_ok, ingest_ok, direct_ok]):
        logger.info("All tests PASSED! The system should be working.")
    else:
        logger.error("Some tests FAILED! Check the logs above for details.")

if __name__ == "__main__":
    main()
