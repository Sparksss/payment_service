FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recomends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/list/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


CMD ["uvcorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]