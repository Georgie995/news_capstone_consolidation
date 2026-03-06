# ─────────────────────────────────────────────────────────────────────────────
# Dockerfile – News Capstone Django Application
# ─────────────────────────────────────────────────────────────────────────────
# Build:   docker build -t news-capstone .
# Run:     docker run -p 8000:8000 -e DJANGO_SECRET_KEY="your-key" news-capstone
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required by mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose the Django development server port
EXPOSE 8000

# Run migrations and start the server
# Using shell form so environment variables are expanded at runtime
CMD cd news_project && \
    python manage.py migrate --noinput && \
    python manage.py runserver 0.0.0.0:8000
