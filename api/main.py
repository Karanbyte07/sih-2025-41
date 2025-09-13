from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import databases
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pika
import json
import os
import asyncio

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:yourpassword@localhost:5432/ocean-db")
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Define the taxonomy table model
taxonomies = sqlalchemy.Table(
    "taxonomies",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, unique=True, index=True),
    sqlalchemy.Column("classification", sqlalchemy.String),
)

Base = declarative_base()
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Ocean Data Platform API",
    description="API for ingesting and visualizing oceanographic data.",
    version="1.0.0"
)

# --- CORS Middleware ---
# This allows the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models (Data Validation) ---
class TaxonomyCreate(BaseModel):
    name: str
    classification: str

# --- RabbitMQ Connection Helper ---
def get_rabbitmq_connection():
    """Establishes a connection to RabbitMQ."""
    connection = None
    for i in range(5): # Retry connection
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'rabbitmq')))
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ connection failed, retrying in {i+1} seconds...")
            asyncio.sleep(i + 1)
    if not connection:
        raise Exception("Could not connect to RabbitMQ.")
    return connection


# --- Background Task for Publishing to RabbitMQ ---
def publish_to_queue(queue_name: str, body: dict):
    """Publishes a message to a specified RabbitMQ queue."""
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(body),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        print(f" [x] Sent message to queue '{queue_name}'")
        connection.close()
    except Exception as e:
        print(f"Error publishing to RabbitMQ: {e}")


# --- API Event Handlers ---
@app.on_event("startup")
async def startup():
    # Retry connecting to the database on startup
    for i in range(5):
        try:
            await database.connect()
            print("Database connection successful.")
            return
        except Exception as e:
            print(f"Database connection failed: {e}. Retrying in {i+1} seconds...")
            await asyncio.sleep(i + 1)
    print("Could not connect to the database. Exiting.")
    # In a real app, you might want to exit or handle this more gracefully
    # For this prototype, we'll let it proceed and fail on requests.

@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
        print("Database connection closed.")


# --- API Endpoints ---

# Root endpoint to serve the frontend
@app.get("/", include_in_schema=False)
async def read_root():
    return FileResponse('frontend/index.html')

# Endpoint to submit taxonomy data
@app.post("/api/ingest/taxonomy", status_code=202)
async def ingest_taxonomy(taxonomy: TaxonomyCreate, background_tasks: BackgroundTasks):
    """
    Accepts taxonomy data and sends it to the 'taxonomy_queue' for processing.
    """
    background_tasks.add_task(publish_to_queue, 'taxonomy_queue', taxonomy.dict())
    return {"message": "Taxonomy data accepted for processing."}

# Endpoint to submit otolith data (placeholder)
@app.post("/api/ingest/otolith", status_code=202)
async def ingest_otolith(background_tasks: BackgroundTasks):
    """
    Accepts otolith data and sends it to the 'otolith_queue' for processing.
    (This is a placeholder and would be expanded to handle file uploads)
    """
    # In a real app, you'd handle file uploads here
    data = {"image_id": "otolith_123.jpg", "timestamp": "2025-09-03T20:10:00Z"}
    background_tasks.add_task(publish_to_queue, 'otolith_queue', data)
    return {"message": "Otolith data accepted for processing."}

# Endpoint to submit eDNA data (placeholder)
@app.post("/api/ingest/edna", status_code=202)
async def ingest_edna(background_tasks: BackgroundTasks):
    """
    Accepts eDNA data and sends it to the 'edna_queue' for processing.
    """
    data = {"sequence_id": "eDNA_seq_456", "location": "Reef_A"}
    background_tasks.add_task(publish_to_queue, 'edna_queue', data)
    return {"message": "eDNA data accepted for processing."}

# Endpoint for visualization data (Step 3)
@app.get("/api/trends/biodiversity")
async def get_biodiversity_trends():
    """
    Retrieves aggregated taxonomy data for frontend visualizations.
    """
    if not database.is_connected:
        raise HTTPException(status_code=503, detail="Database service is unavailable.")
    query = taxonomies.select()
    try:
        results = await database.fetch_all(query)
        # In a real app, you would perform aggregation here.
        # For the prototype, we just return the counts.
        return [{"name": result["name"], "classification": result["classification"]} for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from database: {e}")
