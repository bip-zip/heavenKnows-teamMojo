FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps
RUN apt-get update && apt-get install -y build-essential

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the rest of the project
COPY . .

# Collect static
RUN python app/manage.py collectstatic --noinput || true

EXPOSE 4000

# Correct CMD
CMD ["gunicorn", "--bind", "0.0.0.0:4000", "heavenknows.wsgi:application"]
