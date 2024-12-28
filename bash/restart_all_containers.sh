#!/bin/bash

BASE_DIR="./"
CONFIG_FILE="${BASE_DIR}containers.json"

# Überprüfen, ob die Konfigurationsdatei existiert
if [[ ! -f $CONFIG_FILE ]]; then
    echo "Konfigurationsdatei $CONFIG_FILE nicht gefunden!"
    exit 1
fi

# Docker Compose-Dateien aus der JSON-Konfiguration laden und Container neu starten
containers=$(jq -r 'keys[]' "$CONFIG_FILE")
for container_name in $containers; do
    compose_file=$(jq -r --arg name "$container_name" '.[$name].compose' "$CONFIG_FILE")

    # Pfad relativ zum BASE_DIR auflösen
    compose_file="${BASE_DIR}${compose_file}"

    # Prüfen, ob die docker-compose-Datei existiert
    if [[ ! -f "$compose_file" ]]; then
        echo "Ungültige oder nicht gefundene Docker Compose-Datei: $compose_file"
        continue
    fi

    echo "Stoppe Docker Compose für: $container_name"
    docker compose -f "$compose_file" down

    echo "Starte Docker Compose für: $container_name"
    docker compose -f "$compose_file" up -d

done

echo "Alle Container wurden neu gestartet."
