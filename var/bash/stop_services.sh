#!/bin/bash

BASE_DIR="./"
CONFIG_FILE="${BASE_DIR}services.json"

# Funktion zum Beenden eines Services
stop_service() {
    service_name=$1
    start_command=$(jq -r --arg name "$service_name" '.[$name].command' "$CONFIG_FILE")

    # Suchen und Beenden aller Prozesse, die mit dem Startbefehl übereinstimmen
    echo "Beende Service: $service_name"
    pids=$(pgrep -f "$start_command")

    if [[ -z "$pids" ]]; then
        echo "Service $service_name läuft nicht."
    else
        echo "Beende Prozesse: $pids"
        kill $pids
        echo "Service $service_name wurde gestoppt."
    fi
}

# Funktion zum Stoppen aller oder ausgewählter Services
stop_selected_services() {
    selected_services=("$@") # Liste der ausgewählten Services
    services=$(jq -r 'keys[]' "$CONFIG_FILE") # Alle Service-Namen aus JSON lesen

    for service_name in $services; do
        if [[ ${#selected_services[@]} -eq 0 || " ${selected_services[@]} " =~ " $service_name " ]]; then
            stop_service "$service_name"
        fi
    done
}

# Hauptlogik: Entweder alle oder ausgewählte Services stoppen
if [[ $# -eq 0 ]]; then
    echo "Stoppe alle Services..."
    stop_selected_services
else
    echo "Stoppe ausgewählte Services: $@"
    stop_selected_services "$@"
fi

echo "Alle gewünschten Services wurden gestoppt."
