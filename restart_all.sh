#!/bin/bash

# Datei mit den Pfaden zu den Docker Compose-Dateien
config_file="compose_files.conf"

# Überprüfen, ob die Konfigurationsdatei existiert
if [[ ! -f $config_file ]]; then
    echo "Konfigurationsdatei $config_file nicht gefunden!"
    exit 1
fi

# Docker Compose-Dateien aus der Konfiguration laden und Container neu starten
while IFS= read -r compose_file; do
    echo "Stoppe Docker Compose für: $compose_file"
    docker compose -f $compose_file down

    echo "Starte Docker Compose für: $compose_file"
    docker compose -f $compose_file up -d

done < "$config_file"

echo "Alle Container wurden neu gestartet."
