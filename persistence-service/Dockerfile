# Basis-Image
FROM python:3.10-slim

# Systemabhängigkeiten installieren (kafka)
RUN apt-get update && apt-get install -y \
  gcc \
  librdkafka-dev \
  python3-dev \
  && apt-get clean

# Arbeitsverzeichnis im Container
WORKDIR /app

# Anforderungen kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY . .

# Container-Einstiegspunkt
CMD ["python", "persistence_service.py"]
