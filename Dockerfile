# Multi-stage lightweight Python runtime
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy project files
COPY . .

EXPOSE 5000

CMD ["sh", "-c", "gunicorn wsgi:app --bind 0.0.0.0:${PORT} --workers 2 --threads 4"]

