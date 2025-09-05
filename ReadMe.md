Ocean Data Platform Prototype
This project is a scalable, cloud-ready prototype for an oceanographic data platform. It features a FastAPI backend, a PostgreSQL database, a RabbitMQ message queue for asynchronous data ingestion, and a single-page HTML/JavaScript frontend for data submission and visualization.

The entire application is containerized using Docker and orchestrated with Docker Compose.

Project Structure
/
|-- api/                  # FastAPI backend service
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- main.py
|-- workers/              # Asynchronous data processing services
|   |-- Dockerfile.workers
|   |-- requirements.txt
|   |-- taxonomy_worker.py
|   |-- otolith_worker.py
|   |-- edna_worker.py
|-- frontend/             # Single-page web application
|   |-- index.html
|-- docker-compose.yml    # Orchestrates all services
|-- README.md             

How to Run the Prototype
Prerequisites
Docker

Docker Compose

Step 1: Create the Project Files
Create all the directories and files listed in the project structure and populate them with the code.

Step 2: Build and Run the Services
Navigate to the root directory of the project (where docker-compose.yml is located) in your terminal and run the following command:

docker-compose up --build

This command will:

Build the Docker images for the api and workers services.

Pull the official postgres and rabbitmq images.

Start all the services defined in docker-compose.yml in the correct order.

You will see logs from all the services in your terminal. It might take a minute for all services to start up and become healthy.

Step 3: Access the Web Platform
Once the services are running, open your web browser and navigate to:

http://localhost:8000

You should see the Ocean Data Platform interface.

Step 4: Use the Platform
Ingest Data:

Fill out the Taxonomy Data form and click "Submit". This sends a message to the taxonomy_queue. The taxonomy_worker will consume this message and save the data to the PostgreSQL database.

Click the "Submit Sample Otolith" and "Submit Sample eDNA" buttons to send messages to their respective queues. You can watch the terminal logs for the workers to see them process these mock jobs.

Visualize Data:

The Biodiversity Trends chart will automatically load data from the database.

After you submit new taxonomy data, wait a few seconds and click the "Refresh Data" button to see your new data reflected in the chart.

Accessing Services Directly
API Documentation (Swagger UI): http://localhost:8000/docs

RabbitMQ Management UI: http://localhost:15672 (Login with user: user, password: password)

Step 5: Stopping the Application
To stop all the running containers, press CTRL+C in the terminal where docker-compose up is running. To remove the containers and the database volume, run:

docker-compose down -v

Scalability and Deployment
Scalability: This architecture is horizontally scalable. To handle more traffic, you can run multiple instances of the worker containers. For example, to run 3 taxonomy workers, you could modify the docker-compose.yml or use a deployment platform like Kubernetes.

Deployment: This Docker Compose setup is designed for local development. For production, you would deploy these services to a cloud provider like Render, Heroku, AWS, or Google Cloud, typically using their container services.
