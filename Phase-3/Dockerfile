# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the backend code into the container
COPY backend/ ./backend/

# Copy the main app entry point
COPY app.py .

# Expose the port (FastAPI default is 8000, but Hugging Face uses dynamic ports)
EXPOSE 8000

# Run the application
CMD ["python", "-c", "from app import main; main()"]