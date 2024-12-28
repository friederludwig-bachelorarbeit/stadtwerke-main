FROM python:3.9-slim

# Systemabhängigkeiten installieren (kafka)
RUN apt-get update && apt-get install -y \
  gcc \
  librdkafka-dev \
  python3-dev \
  && apt-get clean

# Arbeitsverzeichnis festlegen
WORKDIR /app

# Abhängigkeiten aus requirements.txt installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code in den Container kopieren
COPY . .

# Container-Startbefehl
CMD ["python", "main.py"]
