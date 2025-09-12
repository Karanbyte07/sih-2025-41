# Use the official Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app/ai_model

# Copy the requirements file and install dependencies
COPY ./ai_model/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the training script and data
COPY ./ai_model/train_model.py .
COPY ./ai_model/sample_training_data.csv .

# The command to run when the container starts
CMD ["python", "train_model.py"]
