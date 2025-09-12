import pika
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import random
import csv

# --- Database setup ---
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "cmlre_data")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
db_connection = None

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)

def setup_database():
    global db_connection
    try:
        db_connection = get_db_connection()
        with db_connection.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS otolith_morphometrics (
                    id SERIAL PRIMARY KEY,
                    image_id VARCHAR(255) UNIQUE NOT NULL,
                    area_px REAL,
                    perimeter_px REAL,
                    width_px INT,
                    height_px INT,
                    aspect_ratio REAL,
                    predicted_species VARCHAR(255),
                    analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            db_connection.commit()
    except psycopg2.OperationalError as e:
        print(f"Database connection failed during setup: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database()
    yield
    if db_connection:
        db_connection.close()

app = FastAPI(lifespan=lifespan)

# --- API Endpoints ---
@app.post("/api/ingest/otolith")
async def ingest_otolith(data: dict):
    channel = pika.BlockingConnection(
        pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'rabbitmq'))
    ).channel()
    channel.queue_declare(queue='otolith_queue', durable=True)
    channel.basic_publish(exchange='', routing_key='otolith_queue', body=json.dumps(data))
    return JSONResponse(content={"message": "Otolith data queued for analysis."})

@app.get("/api/otolith/dashboard_data")
async def get_dashboard_data():
    results = []
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM otolith_morphometrics ORDER BY analysis_timestamp DESC;")
        results = cur.fetchall()
    conn.close()

    # Inject mock locations
    for item in results:
        item['latitude'] = random.uniform(5, 20)
        item['longitude'] = random.uniform(70, 85)

    return results

@app.post("/api/ingest/csv")
async def ingest_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        decoded = contents.decode("utf-8").splitlines()
        reader = csv.DictReader(decoded)

        conn = get_db_connection()
        with conn.cursor() as cur:
            for row in reader:
                cur.execute("""
                    INSERT INTO otolith_morphometrics (image_id, area_px, perimeter_px, width_px, height_px, aspect_ratio, predicted_species)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (image_id) DO NOTHING;
                """, (
                    f"csv-{row['species']}-{row['area_px']}-{row['perimeter_px']}",
                    float(row['area_px']),
                    float(row['perimeter_px']),
                    int(row['width_px']),
                    int(row['height_px']),
                    float(row['aspect_ratio']),
                    row['species']
                ))
        conn.commit()
        conn.close()

        return {"message": "CSV ingested successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
