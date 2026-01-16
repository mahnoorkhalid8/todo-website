FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Update package lists and install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy requirements
COPY backend/requirements.txt .

# Install dependencies with wheel pre-building to handle compilation issues
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --timeout 1200 --only-binary=all psycopg2-binary==2.9.9 && \
    pip install --no-cache-dir --timeout 1200 --prefer-binary -r requirements.txt

# Copy backend code
COPY backend/ .

# Expose port (using 7860 for Hugging Face compatibility, but app can read from env var)
EXPOSE 7860

# Run the application
CMD ["python", "-c", "from app import main; main()"]

# # Use an official Python runtime as a parent image
# FROM python:3.11-slim

# # Set environment variables
# ENV PYTHONUNBUFFERED=1
# ENV PYTHONDONTWRITEBYTECODE=1

# # Set the working directory
# WORKDIR /app

# # Copy the requirements file into the container
# COPY requirements.txt .

# # Install dependencies
# RUN pip install --no-cache-dir --upgrade -r requirements.txt

# # Copy the backend code into the container
# COPY backend/ ./backend/

# # Copy the main app entry point
# COPY app.py .

# # Expose the port (Hugging Face uses dynamic ports)
# EXPOSE 7860

# # Run the application
# CMD ["python", "app.py"]