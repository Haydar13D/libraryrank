FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

RUN chmod +x /app/entrypoint.sh 2>/dev/null || true

# Expose port
EXPOSE 8000

# Entrypoint script ensures SSL certs exist before starting Gunicorn
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--certfile", "/app/cert.pem", "--keyfile", "/app/key.pem", "--workers", "2", "--reload", "libraryrank.wsgi:application"]
