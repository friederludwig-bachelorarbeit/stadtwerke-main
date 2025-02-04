# Zentrales IoT-Datenerfassungssystem für Stadtwerke

Dieses Projekt enthält mehrere Microservices und Container, die mithilfe von Docker Compose und Shell-Skripten orchestriert werden. Die wichtigsten Komponenten sind:

- Kafka-Setup (Kafka und Zookeeper)
- MQTT-Consumer
- Validation-Service
- Persistence-Service (InfluxDB)
- Monitoring mit Grafana

## Voraussetzungen
Stellen Sie sicher, dass die folgenden Tools auf Ihrem System installiert sind:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [jq](https://stedolan.github.io/jq/) (zum Verarbeiten von JSON-Dateien in Shell-Skripten)


#### jq installieren
```bash
# mac os
brew install jq

# windows
choco install jq
```


## 🚀 Erster Start
Führen Sie die folgenden Schritte aus, um das Projekt zum ersten Mal zu starten:

1. **Docker-Netzwerk erstellen**:
    ```bash
    bash docker network create kafka-network
    ```

2. **Docker-Container starten**:
   ```bash
   bash cmd/start_container.sh
   ```

3. **Überprüfen, ob die Container laufen**:
   ```bash
   docker ps
   ```


## 🛑 Dienste stoppen
Um alle Dienste zu stoppen:

- **Container stoppen**:
  ```bash
  bash cmd/stop_container.sh
  ```

## 📊 Grafana Dashboard aufrufen
Das System ist jetzt bereit und empfängt eingehende Nachrichten.

🔗 Grafana Dashboard: http://localhost:3000/

Falls die Daten im Dashboard nicht sofort angezeigt werden:

1. Öffne das Grafana Dashboard.
2. Klicke bei einer Kachel auf "Bearbeiten".
3. Warte einen kurzen Moment – die Nachrichten sollten nun erscheinen.

## 📃 Verfügbare Shell-Skripte
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
