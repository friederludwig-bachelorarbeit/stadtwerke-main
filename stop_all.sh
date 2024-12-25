#!/bin/bash

# Array mit den Pfaden zu den Docker Compose-Dateien
compose_files=(
    "kafka-setup/docker-compose.yml"
    "mqtt-consumer/docker-compose.yml"
    "validation-service/docker-compose.yml"
    "persistence-service/docker-compose.yml"
)

# Alle Docker Compose-Dateien stoppen
for compose_file in "${compose_files[@]}"; do
    echo "Stoppe Docker Compose für: $compose_file"
    docker compose -f $compose_file down
done

echo "Alle Container wurden gestoppt."
