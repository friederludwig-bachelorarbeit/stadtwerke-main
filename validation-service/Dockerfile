# Basis-Image
FROM python:3.9-slim

# Systemabhängigkeiten installieren (kafka)
RUN apt-get update && apt-get install -y \
  gcc \
  librdkafka-dev \
  python3-dev \
  iputils-ping \       
  && apt-get clean

# Arbeitsverzeichnis festlegen
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code in den Container kopieren
COPY . .

# Standardbefehl zum Starten des Validation-Service
CMD ["python", "validation_service.py"]
