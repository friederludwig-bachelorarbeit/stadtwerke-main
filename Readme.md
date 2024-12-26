# Zentrales IoT-Datenerfassungssystem für Stadtwerke

Dieses Projekt enthält mehrere Microservices und Container, die mithilfe von Docker Compose und Shell-Skripten orchestriert werden. Die wichtigsten Komponenten sind:

- Kafka-Setup (Kafka und Zookeeper)
- MQTT-Consumer
- Validation-Service
- Persistence-Service (InfluxDB)

## Voraussetzungen
Stellen Sie sicher, dass die folgenden Tools auf Ihrem System installiert sind:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [jq](https://stedolan.github.io/jq/) (zum Verarbeiten von JSON-Dateien in Shell-Skripten)


## Verfügbare Shell-Skripte
Die Shell-Skripte befinden sich im Verzeichnis `var/bash/...` und können mit `bash` ausgeführt werden. Sie dienen der Verwaltung der Services und Container:

### 1. **`start_container.sh`**
Startet alle oder ausgewählte Docker-Container basierend auf der `container.json`. Beispiel:

- **Alle Container starten**:
  ```bash
  bash var/bash/start_container.sh
  ```
- **Einen bestimmten Container starten**:
  ```bash
  bash var/bash/start_container.sh mqtt-consumer
  ```

### 2. **`stop_container.sh`**
Stoppt alle oder ausgewählte Docker-Container basierend auf der `container.json`. Beispiel:

- **Alle Container stoppen**:
  ```bash
  bash var/bash/stop_container.sh
  ```
- **Einen bestimmten Container stoppen**:
  ```bash
  bash var/bash/stop_container.sh mqtt-consumer
  ```

### 3. **`restart_all_containers.sh`**
Startet alle Container neu, indem sie gestoppt und wieder hochgefahren werden. Beispiel:

```bash
bash var/bash/restart_all_containers.sh
```

### 4. **`start_services.sh`**
Startet alle oder ausgewählte Microservices basierend auf der `services.json`. Dabei werden virtuelle Umgebungen verwaltet und die Services ausgeführt. Beispiel:

- **Alle Services starten**:
  ```bash
  bash var/bash/start_services.sh
  ```
- **Einen bestimmten Service starten**:
  ```bash
  bash var/bash/start_services.sh validation-service
  ```

### 5. **`stop_services.sh`**
Stoppt alle oder ausgewählte Microservices basierend auf der `services.json`. Beispiel:

- **Alle Services stoppen**:
  ```bash
  bash var/bash/stop_services.sh
  ```
- **Einen bestimmten Service stoppen**:
  ```bash
  bash var/bash/stop_services.sh validation-service
  ```

## JSON-Konfigurationsdateien
Damit die Skripte funktionieren, sind die folgenden JSON-Dateien erforderlich:

### 1. **`services.json`**
Definiert alle Microservices: die virtuellen Umgebungen und Startbefehle. Beispiel:

```json
{
  "mqtt-consumer": {
    "venv": "mqtt-consumer/venv",
    "command": "python mqtt-consumer/main.py"
  },
  "validation-service": {
    "venv": "validation-service/venv",
    "command": "python validation-service/main.py"
  }
}
```

### 2. **`container.json`**
Definiert alle Docker Compose-Dateien für die Container. Beispiel:

```json
{
  "mqtt-consumer": {
    "compose": "mqtt-consumer/docker-compose.yml"
  },
  "influxdb": {
    "compose": "persistence-service/docker-compose.yml"
  }
}
```

## Erster Start
Führen Sie die folgenden Schritte aus, um das Projekt zum ersten Mal zu starten:

1. **Docker-Container starten**:
   ```bash
   bash var/bash/start_container.sh
   ```

2. **Überprüfen, ob die Container laufen**:
   ```bash
   docker ps
   ```

3. **Microservices starten**:
   ```bash
   bash var/bash/start_services.sh
   ```

## Dienste stoppen
Um alle Dienste zu stoppen:

- **Container stoppen**:
  ```bash
  bash var/bash/stop_container.sh
  ```

- **Microservices stoppen**:
  ```bash
  bash var/bash/stop_services.sh
  ```