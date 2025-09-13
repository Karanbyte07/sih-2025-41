import os
import time
import logging
import json # <--- THIS IS THE FIX
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pika
from sqlalchemy import create_engine, text, inspect
from contextlib import asynccontextmanager

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/cmlre_data")
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# --- Database Setup on Startup ---
def setup_database_and_tables():
    logger.info("Attempting to connect to the database...")
    max_retries = 20
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                logger.info("Database connection successful.")
                inspector = inspect(engine)
                if not inspector.has_table("otolith_morphometrics"):
                    logger.info("Table 'otolith_morphometrics' does not exist. Creating it now.")
                    create_table_query = text("""
                        CREATE TABLE otolith_morphometrics (
                            id SERIAL PRIMARY KEY,
                            image_id VARCHAR(255) UNIQUE NOT NULL,
                            area FLOAT, perimeter FLOAT, width FLOAT, height FLOAT, aspect_ratio FLOAT,
                            predicted_species VARCHAR(255), latitude FLOAT, longitude FLOAT,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                    connection.execute(create_table_query)
                    connection.commit()
                    logger.info("Table 'otolith_morphometrics' created successfully.")
                else:
                    logger.info("Table 'otolith_morphometrics' already exists.")
                return
        except Exception as e:
            logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise RuntimeError("Failed to connect to the database after multiple retries.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database_and_tables()
    yield

# --- FastAPI App ---
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

class OtolithIngest(BaseModel):
    image_data: str
    image_id: str

@app.post("/api/ingest/otolith")
def ingest_otolith(item: OtolithIngest):
    logger.info(f"Received otolith ingest request for image_id: {item.image_id}")
    
    # Validate that image_data is provided
    if not item.image_data:
        logger.error(f"No image data provided for image_id: {item.image_id}")
        raise HTTPException(status_code=400, detail="Image data is required")
    
    try:
        # Test RabbitMQ connection first
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='otolith_queue', durable=True)
        
        # Use the actual image data from the request, not hardcoded data
        message_data = {"image_id": item.image_id, "image_data": item.image_data}
        message_body = json.dumps(message_data)
        
        # Publish to queue
        channel.basic_publish(
            exchange='', 
            routing_key='otolith_queue', 
            body=message_body,
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
        connection.close()
        
        logger.info(f"Successfully queued message for image_id: {item.image_id} with data length: {len(item.image_data)}")
        return {"status": "success", "message": "Image queued for processing."}
        
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"RabbitMQ connection failed for {item.image_id}: {e}")
        raise HTTPException(status_code=503, detail="Message queue service unavailable")
    except Exception as e:
        logger.error(f"Failed to queue message for {item.image_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/data")
def get_dashboard_data():
    try:
        with engine.connect() as connection:
            query = text("SELECT image_id, predicted_species, area, perimeter, width, height, aspect_ratio, latitude, longitude, created_at FROM otolith_morphometrics ORDER BY created_at DESC;")
            result = connection.execute(query)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch data from database.")