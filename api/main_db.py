import pika
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import time

# --- Database Configuration ---
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# Global variable to hold the database connection pool
db_connection = None

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def setup_database():
    """Initializes the database connection and creates tables if they don't exist."""
    global db_connection
    retries = 10
    while retries > 0:
        try:
            print("Attempting to connect to the database...")
            db_connection = get_db_connection()
            with db_connection.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS taxonomy (
                        id SERIAL PRIMARY KEY,
                        scientific_name VARCHAR(255) NOT NULL,
                        common_name VARCHAR(255),
                        sighting_count INT DEFAULT 1,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS otolith_morphometrics (
                        id SERIAL PRIMARY KEY,
                        image_id VARCHAR(255) UNIQUE NOT NULL,
                        area_px REAL,
                        perimeter_px REAL,
                        width_px INT,
                        height_px INT,
                        aspect_ratio REAL,
                        analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                db_connection.commit()
            print("Database connection successful and tables are set up.")
            break
        except psycopg2.OperationalError as e:
            print(f"Database connection failed: {e}. Retrying in 5 seconds...")
            retries -= 1
            time.sleep(5)
    if not db_connection:
        raise Exception("Could not connect to the database after several retries.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    setup_database()
    yield
    # On shutdown
    if db_connection:
        db_connection.close()
        print("Database connection closed.")

app = FastAPI(lifespan=lifespan)

# --- RabbitMQ Connection ---
def get_rabbitmq_channel():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    return connection.channel()

# --- API Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def read_root():
    # In a real-world scenario, you would serve the index_db.html file
    # For this simplified example, we confirm the API is running.
    return "<h1>CMLRE Platform API (DB-Enabled) is running.</h1>"

@app.post("/api/ingest/taxonomy")
async def ingest_taxonomy(data: dict):
    channel = get_rabbitmq_channel()
    channel.queue_declare(queue='taxonomy_queue', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='taxonomy_queue',
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2) # make message persistent
    )
    return JSONResponse(content={"message": "Taxonomy data queued for ingestion."})

@app.post("/api/ingest/otolith")
async def ingest_otolith(data: dict):
    channel = get_rabbitmq_channel()
    channel.queue_declare(queue='otolith_queue', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='otolith_queue',
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    return JSONResponse(content={"message": "Otolith data queued for analysis."})

@app.post("/api/ingest/edna")
async def ingest_edna(data: dict):
    channel = get_rabbitmq_channel()
    channel.queue_declare(queue='edna_queue', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='edna_queue',
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    return JSONResponse(content={"message": "eDNA data queued for processing."})

@app.get("/api/trends/biodiversity")
async def get_biodiversity_trends():
    with db_connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT common_name, sighting_count AS count FROM taxonomy ORDER BY sighting_count DESC LIMIT 10;")
        results = cur.fetchall()
    return results

@app.get("/api/otolith/results/{image_id}")
async def get_otolith_results(image_id: str):
    """New endpoint to fetch otolith analysis results from the database."""
    with db_connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM otolith_morphometrics WHERE image_id = %s;", (image_id,))
        result = cur.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Results not found for this image ID.")
    return result
