# Zentrales IoT-Datenerfassungssystem
Dieses Projekt enthält mehrere Microservices, die mit Docker Compose orchestriert werden. Dazu gehören:

- Kafka-Setup (Kafka und Zookeeper)
- MQTT-Consumer
- Validation-Service
- Persistence-Service (InfluxDB)


## Voraussetzungen
Stellen Sie sicher, dass die folgenden Tools auf Ihrem System installiert sind:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Erster Start
Wenn Sie das Repository das erste Mal klonen, folgen Sie diesen Schritten:

#### Shell-Skript ausführbar machen:
Das Skript start_all.sh ist dafür zuständig, alle Docker-Container zu starten. Machen Sie das Skript ausführbar:

```bash
chmod +x start_all.sh
chmod +x stop_all.sh
```

#### Docker-Container starten:
Starten Sie alle Docker-Container im Hintergrund (detached mode) mit:
```bash
./start_all.sh
```

#### Überprüfung:
Stellen Sie sicher, dass alle Container laufen:

```bash
docker ps
```
