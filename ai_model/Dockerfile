FROM python:3.10-slim

WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY ai_model/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a data directory and copy the training data
COPY ai_model/sample_training_data.csv ./data/

# Copy the rest of the application code
COPY ai_model/ .

# Command to run the training script
CMD ["python", "train_model.py"]
