#!/bin/bash

BASE_DIR="./"  


# Zentrale Log-Datei
LOG_DIR="var/logs"
LOG_FILE_NAME="global.log"
combined_log="$LOG_DIR/$LOG_FILE_NAME"

CONFIG_FILE="${BASE_DIR}services.json"

# Stellt sicher, dass das Log-Verzeichnis existiert
mkdir -p "$LOG_DIR"

# Funktion zum Starten eines Services
start_service() {
    service_name=$1
    venv_path=$(jq -r --arg name "$service_name" '.[$name].venv' "$CONFIG_FILE")
    start_command=$(jq -r --arg name "$service_name" '.[$name].command' "$CONFIG_FILE")
    
    # Pfade relativ zum BASE_DIR auflösen
    service_dir=$(dirname "$venv_path")  # Das Verzeichnis des venv
    venv_path="$BASE_DIR$venv_path"
    requirements_file="$service_dir/requirements.txt"
    start_command="cd $BASE_DIR && $start_command"

    echo "Starte Service: $service_name"

    # Überprüfen, ob die virtuelle Umgebung existiert
    if [[ ! -d "$venv_path" ]]; then
        echo "Virtuelle Umgebung für $service_name wird erstellt..."
        python3 -m venv "$venv_path"
        echo "Virtuelle Umgebung erstellt: $venv_path"

        # Installiere Abhängigkeiten aus requirements.txt, falls vorhanden
        if [[ -f "$requirements_file" ]]; then
            echo "Installiere Abhängigkeiten für $service_name..."
            source "$venv_path/bin/activate"
            pip install -r "$requirements_file"
            deactivate
        else
            echo "WARNUNG: Keine requirements.txt für $service_name gefunden."
        fi
    fi

    # Starten des Services
    (
        source "$venv_path/bin/activate"
        nohup bash -c "$start_command 2>&1 | while IFS= read -r line; do echo \"[$(date '+%Y-%m-%d %H:%M:%S')] [$service_name] \$line\"; done" >> "$LOG_DIR/$LOG_FILE_NAME" &
    )
}


# Funktion zum Lesen der JSON-Datei und Starten der Services
start_selected_services() {
    selected_services=("$@") # Liste der ausgewählten Services
    services=$(jq -r 'keys[]' "$CONFIG_FILE") # Alle Service-Namen aus JSON lesen

    for service_name in $services; do
        if [[ ${#selected_services[@]} -eq 0 || " ${selected_services[@]} " =~ " $service_name " ]]; then
            venv_path=$(jq -r --arg name "$service_name" '.[$name].venv' "$CONFIG_FILE")
            start_command=$(jq -r --arg name "$service_name" '.[$name].command' "$CONFIG_FILE")
            start_service "$service_name" "$venv_path" "$start_command"
        fi
    done
}

# Hauptlogik: Entweder alle oder ausgewählte Services starten
if [[ $# -eq 0 ]]; then
    echo "Starte alle Services..."
    start_selected_services
else
    echo "Starte ausgewählte Services: $@"
    start_selected_services "$@"
fi

echo "Alle ausgewählten Services wurden gestartet. Zentrale Logs befinden sich in: $combined_log"
