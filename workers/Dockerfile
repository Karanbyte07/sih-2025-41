FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app/workers

# Copy the single, consolidated requirements file
COPY ./workers/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the worker code
COPY ./workers .

# The command to run will be specified in docker-compose.yml
