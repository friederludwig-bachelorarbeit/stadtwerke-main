#!/bin/bash

BASE_DIR="./"
CONFIG_FILE="${BASE_DIR}containers.json"

# Funktion zum Stoppen eines Docker-Compose-Containers
stop_container() {
    container_name=$1
    compose_file=$(jq -r --arg name "$container_name" '.[$name].compose' "$CONFIG_FILE")

    # Pfad relativ zum BASE_DIR auflösen
    compose_file="${compose_file}"

    # Prüfen, ob die docker-compose-Datei existiert
    if [[ ! -f "$compose_file" ]]; then
        echo "Fehler: docker-compose-Datei für $container_name nicht gefunden: $compose_file"
        return 1
    fi

    echo "Stoppe Container: $container_name mit docker-compose-Datei: $compose_file"
    docker compose -f "$compose_file" down
}

# Funktion zum Stoppen aller oder ausgewählter Docker-Compose-Container
stop_selected_containers() {
    selected_containers=("$@") 
    # Alle Container-Namen aus JSON lesen
    containers=$(jq -r 'keys[]' "$CONFIG_FILE") 

    for container_name in $containers; do
        if [[ ${#selected_containers[@]} -eq 0 || " ${selected_containers[@]} " =~ " $container_name " ]]; then
            stop_container "$container_name"
        fi
    done
}

# Hauptlogik: Entweder alle oder ausgewählte Container stoppen
if [[ $# -eq 0 ]]; then
    echo "Stoppe alle Container..."
    stop_selected_containers
else
    echo "Stoppe ausgewählte Container: $@"
    stop_selected_containers "$@"
fi

echo "Alle gewünschten Container wurden gestoppt."
