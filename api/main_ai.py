import pika
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

# ... (Database setup and FastAPI lifespan is identical to main_db.py) ...
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database()
    yield
    if db_connection: db_connection.close()

app = FastAPI(lifespan=lifespan)
# ... (All ingestion endpoints are identical to main_db.py) ...
@app.post("/api/ingest/otolith")
async def ingest_otolith(data: dict):
    # ... (identical) ...
    channel = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'rabbitmq'))).channel()
    channel.queue_declare(queue='otolith_queue', durable=True)
    channel.basic_publish(exchange='', routing_key='otolith_queue', body=json.dumps(data))
    return JSONResponse(content={"message": "Otolith data queued for analysis."})

@app.get("/api/trends/biodiversity")
async def get_biodiversity_trends():
    # ... (identical) ...
    with db_connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT common_name, sighting_count AS count FROM taxonomy LIMIT 10;")
        return cur.fetchall()

@app.get("/api/otolith/results/{image_id}")
async def get_otolith_results(image_id: str):
    """UPDATED: Now also fetches the predicted_species field."""
    with db_connection.cursor(cursor_factory=RealDictCursor) as cur:
        # The ai_worker adds this column, so we select it.
        # Use a LEFT JOIN to ensure we get a result even before the prediction is ready.
        cur.execute("""
            SELECT *, COALESCE(predicted_species, 'Pending Prediction...') as predicted_species
            FROM otolith_morphometrics 
            WHERE image_id = %s;
        """, (image_id,))
        result = cur.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Results not found for this image ID.")
    return result
