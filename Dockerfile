# Dockerfile
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy the Django project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 4000

# Start Gunicorn server
CMD ["gunicorn", "app.heavenknows.wsgi:application", "--bind", "0.0.0.0:4000"]
