# -------------------------------
# Base image
# -------------------------------
FROM python:3.9-slim

# -------------------------------
# Set working directory
# -------------------------------
WORKDIR /app

# -------------------------------
# Install system dependencies
# -------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Copy requirements and install
# -------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Copy API source code
# -------------------------------
COPY . .

# -------------------------------
# Expose API port
# -------------------------------
EXPOSE 8000

# -------------------------------
# Run FastAPI with Uvicorn
# -------------------------------
CMD ["uvicorn", "mainfinal:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
