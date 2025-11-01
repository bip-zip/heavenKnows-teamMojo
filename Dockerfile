FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn

# Copy the rest of the project
COPY . .

# Collect static files (ignore errors if settings not ready)
RUN python manage.py collectstatic --noinput || true

EXPOSE 4400

# Run Gunicorn on port 4400
CMD ["gunicorn", "--bind", "0.0.0.0:4400", "heavenknows.wsgi:application"]
