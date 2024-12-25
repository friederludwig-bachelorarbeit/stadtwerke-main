#!/bin/bash

# Array mit den Pfaden zu den Docker Compose-Dateien
compose_files=(
    "kafka-setup/docker-compose.yml"
    "mqtt-consumer/docker-compose.yml"
    "validation-service/docker-compose.yml"
    "persistence-service/docker-compose.yml"
)

# Alle Docker Compose-Dateien starten
for compose_file in "${compose_files[@]}"; do
    echo "Starte Docker Compose für: $compose_file"
    docker compose -f $compose_file up --build -d
done

echo "Alle Container wurden gestartet."
