# CMLRE Ocean Data Platform - AI Model Builder
# This container builds and trains the species classification model for otolith analysis

# Use the official Python image with scientific computing libraries
FROM python:3.9-slim

# Set environment variables for better Python performance
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /app/ai_model

# Install system dependencies required for machine learning libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY ./ai_model/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the training script and sample data
COPY ./ai_model/train_model.py .
COPY ./ai_model/sample_training_data.csv .

# Create a directory for the trained model output
RUN mkdir -p /app/ai_model/output

# Set the default command to train the model
# This will create the species_classifier.pkl file that the AI worker needs
CMD ["python", "train_model.py"]