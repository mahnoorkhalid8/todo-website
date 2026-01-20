FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Update package lists and install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    musl-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Create a clean requirements file without comments
RUN grep -v '^#' requirements.txt | grep -v '^$' > requirements_clean.txt

# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install packages individually to identify problematic ones
RUN pip install --no-cache-dir --timeout 1200 fastapi==0.104.1
RUN pip install --no-cache-dir --timeout 1200 "uvicorn[standard]==0.24.0"
RUN pip install --no-cache-dir --timeout 1200 sqlmodel==0.0.14
RUN pip install --no-cache-dir --timeout 1200 pydantic[email]==2.5.0
RUN pip install --no-cache-dir --timeout 1200 pydantic-core==2.14.0
RUN pip install --no-cache-dir --timeout 1200 pydantic-settings==2.1.0
RUN pip install --no-cache-dir --timeout 1200 email-validator==2.2.0
RUN pip install --no-cache-dir --timeout 1200 idna==3.7
RUN pip install --no-cache-dir --timeout 1200 python-jose[cryptography]==3.3.0
RUN pip install --no-cache-dir --timeout 1200 passlib[bcrypt]==1.7.4
RUN pip install --no-cache-dir --timeout 1200 bcrypt==4.0.1
RUN pip install --no-cache-dir --timeout 1200 python-multipart==0.0.6
RUN pip install --no-cache-dir --timeout 1200 alembic==1.13.1
RUN pip install --no-cache-dir --timeout 1200 sqlalchemy==2.0.23
# Try installing psycopg2 instead of psycopg2-binary for better compatibility
RUN pip install --no-cache-dir --timeout 1200 psycopg2==2.9.9
RUN pip install --no-cache-dir --timeout 1200 python-dotenv==1.0.0
RUN pip install --no-cache-dir --timeout 1200 httpx==0.25.2

# Copy all the backend files directly to the app directory
COPY backend/ .

# Copy the container-specific app file to the container
COPY app_container.py ./app.py

# Expose port (using 7860 for Hugging Face compatibility)
EXPOSE 7860

# Run the application - using the container-optimized version
CMD ["python", "app.py"]