#!/bin/bash

# Datei mit Container-Definitionen
CONTAINERS_FILE="./containers.json"

# Überprüfen, ob die JSON-Datei existiert
if [[ ! -f "$CONTAINERS_FILE" ]]; then
    echo "Die Datei containers.json wurde nicht gefunden! Bitte überprüfen Sie den Pfad."
    exit 1
fi

# jq wird benötigt, um JSON-Dateien zu parsen
if ! command -v jq &> /dev/null; then
    echo "Das Tool 'jq' ist nicht installiert. Bitte installieren Sie es, um fortzufahren."
    exit 1
fi

# Container-Namen aus der JSON-Datei extrahieren
CONTAINER_NAMES=$(jq -r 'keys[]' "$CONTAINERS_FILE")

# Funktion: Liste der Container anzeigen
select_container() {
    echo "Verfügbare Container:"
    echo "====================="
    echo "$CONTAINER_NAMES" | nl
    echo
    read -p "Wählen Sie die Nummer des Containers (oder mehrere durch Leerzeichen getrennt): " choices
    echo
    SELECTED_CONTAINERS=()
    for choice in $choices; do
        container_name=$(echo "$CONTAINER_NAMES" | sed -n "${choice}p")
        if [[ -n "$container_name" ]]; then
            SELECTED_CONTAINERS+=("$container_name")
        else
            echo "Ungültige Auswahl: $choice"
        fi
    done
    echo "Sie haben folgende Container ausgewählt: ${SELECTED_CONTAINERS[@]}"
}

# Funktion: Container stoppen und neu starten
stop_container() {
    echo "Stopping container: $1 for $2 seconds"
    docker compose -f $(jq -r --arg name "$1" '.[$name].compose' "$CONTAINERS_FILE") stop
    sleep $2 # Dauer des Ausfalls
    docker compose -f $(jq -r --arg name "$1" '.[$name].compose' "$CONTAINERS_FILE") start
    echo "Container $1 restarted."
}

# Funktion: Container pausieren
pause_container() {
    echo "Pausing container: $1 for $2 seconds"
    docker compose -f $(jq -r --arg name "$1" '.[$name].compose' "$CONTAINERS_FILE") pause
    sleep $2 # Dauer des Ausfalls
    docker compose -f $(jq -r --arg name "$1" '.[$name].compose' "$CONTAINERS_FILE") unpause
    echo "Container $1 resumed."
}

# Funktion: Netzwerkprobleme simulieren
network_disrupt() {
    echo "Simulating network issues for container: $1 for $2 seconds"
    container_id=$(docker ps --filter "name=$1" --format "{{.ID}}")
    if [[ -z "$container_id" ]]; then
        echo "Container $1 ist nicht aktiv. Netzwerkstörung kann nicht simuliert werden."
        return
    fi
    docker network disconnect bridge "$container_id"
    sleep $2 # Dauer des Ausfalls
    docker network connect bridge "$container_id"
    echo "Network reconnected for container $1."
}

# Funktion: Ressourcenlimit setzen
limit_resources() {
    echo "Limiting resources for container: $1"
    container_id=$(docker ps --filter "name=$1" --format "{{.ID}}")
    if [[ -z "$container_id" ]]; then
        echo "Container $1 ist nicht aktiv. Ressourcenlimit kann nicht gesetzt werden."
        return
    fi
    docker update --cpus="0.5" --memory="256m" "$container_id"
    echo "CPU und RAM für Container $1 begrenzt."
}

# Hauptmenü
echo "Chaos Testing Script"
echo "===================="
select_container

if [[ ${#SELECTED_CONTAINERS[@]} -eq 0 ]]; then
    echo "Keine Container ausgewählt. Beenden."
    exit 0
fi

read -p "Geben Sie die Dauer des Ausfalls in Sekunden ein: " duration
if ! [[ "$duration" =~ ^[0-9]+$ ]]; then
    echo "Ungültige Eingabe. Bitte geben Sie eine Zahl ein."
    exit 1
fi

echo
echo "1. Stop Container"
echo "2. Pause Container"
echo "3. Simulate Network Issues"
echo "4. Limit Resources"
echo "5. Random Chaos Test"

read -p "Wählen Sie eine Aktion: " action

for container in "${SELECTED_CONTAINERS[@]}"; do
    case $action in
        1) stop_container $container $duration ;;
        2) pause_container $container $duration ;;
        3) network_disrupt $container $duration ;;
        4) limit_resources $container ;;
        5) 
            case $((RANDOM % 3)) in
                0) stop_container $container $duration ;;
                1) pause_container $container $duration ;;
                2) network_disrupt $container $duration ;;
            esac
            ;;
        *) echo "Ungültige Aktion. Beenden." ;;
    esac
done
