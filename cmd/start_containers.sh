#!/bin/bash

BASE_DIR="./"
CONFIG_FILE="${BASE_DIR}containers.json"

# Funktion zum Starten eines Docker-Compose-Containers
start_container() {
    container_name=$1
    compose_file=$(jq -r --arg name "$container_name" '.[$name].compose' "$CONFIG_FILE")

    # Pfad relativ zum BASE_DIR auflösen
    compose_file="${compose_file}"

    # Prüfen, ob die docker-compose-Datei existiert
    if [[ ! -f "$compose_file" ]]; then
        echo "Fehler: docker-compose-Datei für $container_name nicht gefunden: $compose_file"
        return 1
    fi

    echo "Starte Container: $container_name mit docker-compose-Datei: $compose_file"
    docker compose -f "$compose_file" up -d
}

# Funktion zum Starten aller oder ausgewählter Docker-Compose-Container
start_selected_containers() {
    selected_containers=("$@") # Liste der ausgewählten Container
    containers=$(jq -r 'keys[]' "$CONFIG_FILE") # Alle Container-Namen aus JSON lesen

    for container_name in $containers; do
        if [[ ${#selected_containers[@]} -eq 0 || " ${selected_containers[@]} " =~ " $container_name " ]]; then
            start_container "$container_name"
        fi
    done
}

# Hauptlogik: Entweder alle oder ausgewählte Container starten
if [[ $# -eq 0 ]]; then
    echo "Starte alle Container..."
    start_selected_containers
else
    echo "Starte ausgewählte Container: $@"
    start_selected_containers "$@"
fi

echo "Alle gewünschten Container wurden gestartet."
