FROM python:3.12-slim

# Keep Python output visible in the hosting logs.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV DEBUG=False
ENV ALLOWED_HOSTS=.koyeb.app,localhost,127.0.0.1,testserver

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Static files are collected at build time. Database setup happens at startup
# because free preview services may start from a fresh filesystem.
RUN python manage.py collectstatic --noinput
RUN chmod +x /app/start-koyeb.sh

CMD ["/app/start-koyeb.sh"]
