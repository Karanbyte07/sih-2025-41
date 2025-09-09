import pika
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import random

# --- (Database setup and FastAPI lifespan is identical to the previous version) ---
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "cmlre_data")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
db_connection = None

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)

def setup_database():
    global db_connection
    # ... (setup_database logic is identical) ...
    try:
        db_connection = get_db_connection()
        with db_connection.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS otolith_morphometrics (
                    id SERIAL PRIMARY KEY, image_id VARCHAR(255) UNIQUE NOT NULL,
                    area_px REAL, perimeter_px REAL, width_px INT, height_px INT,
                    aspect_ratio REAL, analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            db_connection.commit()
    except psycopg2.OperationalError as e:
        print(f"Database connection failed during setup: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database()
    yield
    if db_connection: db_connection.close()

app = FastAPI(lifespan=lifespan)

# --- (Ingestion and individual result endpoints are identical to main_ai.py) ---
@app.post("/api/ingest/otolith")
async def ingest_otolith(data: dict):
    # This logic remains the same
    channel = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'rabbitmq'))).channel()
    channel.queue_declare(queue='otolith_queue', durable=True)
    channel.basic_publish(exchange='', routing_key='otolith_queue', body=json.dumps(data))
    return JSONResponse(content={"message": "Otolith data queued for analysis."})


@app.get("/api/otolith/dashboard_data")
async def get_dashboard_data():
    """
    UPDATED: Fetches all results and injects mock latitude/longitude
    for the interactive map visualization.
    """
    results = []
    with db_connection.cursor(cursor_factory=RealDictCursor) as cur:
        # Check if the predicted_species column exists
        cur.execute("""
            SELECT EXISTS (
               SELECT 1 FROM information_schema.columns
               WHERE table_name = 'otolith_morphometrics' AND column_name = 'predicted_species'
            );
        """)
        has_prediction_column = cur.fetchone()['exists']

        if has_prediction_column:
            cur.execute("SELECT * FROM otolith_morphometrics ORDER BY analysis_timestamp DESC;")
            results = cur.fetchall()
        else:
            cur.execute("SELECT *, 'N/A' as predicted_species FROM otolith_morphometrics ORDER BY analysis_timestamp DESC;")
            results = cur.fetchall()

    # Inject mock location data for demo purposes
    for item in results:
        # Simulate sample locations around the Indian Ocean
        item['latitude'] = random.uniform(5, 20)
        item['longitude'] = random.uniform(70, 85)

    return results

