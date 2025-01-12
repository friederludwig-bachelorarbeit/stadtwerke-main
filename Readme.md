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

## Erster Start
Führen Sie die folgenden Schritte aus, um das Projekt zum ersten Mal zu starten:

```bash
bash docker network create kafka-network
```

# Grafana Tempo

/explore?schemaVersion=1&panes=%7B%22bo2%22:%7B%22datasource%22:%22be9oo252k21hcc%22,%22queries%22:%5B%7B%22query%22:%22${__data.fields["traceID"]}%22,%22queryType%22:%22traceql%22,%22refId%22:%22A%22,%22limit%22:20,%22tableType%22:%22traces%22,%22filters%22:%5B%7B%22id%22:%22c4ab1bed%22,%22operator%22:%22%3D%22,%22scope%22:%22span%22%7D%5D%7D%5D,%22range%22:%7B%22from%22:%221736609019562%22,%22to%22:%221736612619562%22%7D%7D%7D&orgId=1


1. **Docker-Container starten**:
   ```bash
   bash cmd/start_container.sh
   ```

2. **Überprüfen, ob die Container laufen**:
   ```bash
   docker ps
   ```

## Dienste stoppen
Um alle Dienste zu stoppen:

- **Container stoppen**:
  ```bash
  bash cmd/stop_container.sh
  ```


## Verfügbare Shell-Skripte
Die Shell-Skripte befinden sich im Verzeichnis `cmd/...` und können mit `bash` ausgeführt werden. Sie dienen der Verwaltung der Services und Container:

### 1. **`start_container.sh`**
Startet alle oder ausgewählte Docker-Container basierend auf der `container.json`. 

- **Alle Container starten**:
  ```bash
  bash cmd/start_container.sh
  ```
- **Einen bestimmten Container starten**:
  ```bash
  bash cmd/start_container.sh <container-name>
  ```

### 2. **`stop_container.sh`**
Stoppt alle oder ausgewählte Docker-Container basierend auf der `container.json`.

- **Alle Container stoppen**:
  ```bash
  bash cmd/stop_container.sh
  ```
- **Einen bestimmten Container stoppen**:
  ```bash
  bash cmd/stop_container.sh <container-name>
  ```

### 3. **`restart_all_containers.sh`**
Startet alle Container neu, indem sie gestoppt und wieder hochgefahren werden.

```bash
bash cmd/restart_all_containers.sh
```

## JSON-Konfigurationsdateien
Damit die `bash` Skripte funktionieren, müssen die Container über die JSON-Dateie definiert werden:

### **`container.json`**
Definiert alle Docker Compose-Dateien für die Container.
<br/> Beispiel:

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
