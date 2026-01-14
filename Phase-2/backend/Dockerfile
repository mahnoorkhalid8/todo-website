# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies that might be needed
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies with specific order for email-validator
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir email-validator==2.2.0 && \
    pip install --no-cache-dir idna==3.7 && \
    pip install --no-cache-dir -r requirements.txt

# Copy the backend code into the container
COPY . .

# Expose the port (Hugging Face uses dynamic ports)
EXPOSE 7860

# Run the application
CMD ["python", "app.py"]