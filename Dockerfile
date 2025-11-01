# Dockerfile
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files
RUN python app/manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "app.heavenknows.wsgi:application", "--bind", "0.0.0.0:8000"]
