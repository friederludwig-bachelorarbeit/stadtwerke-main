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

#### Dienste stoppen:
Um alle laufenden Dienste zu stoppen, verwenden Sie das Skript stop_all.sh:
```bash
./stop_all.sh
```

## Weitere Starts
Sobald Sie das Skript start_all.sh ausführbar gemacht haben, können Sie es bei jedem weiteren Start einfach ausführen:

```bash
./start_all.sh
```
Das Skript baut die Docker-Images bei Bedarf neu und startet die Container.