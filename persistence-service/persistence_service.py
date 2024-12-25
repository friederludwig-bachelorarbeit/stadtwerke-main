import os
import json
from confluent_kafka import Consumer
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Konfiguration
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "validated-messages"

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "DF1TBbibSo5P3FC5c5buuaPfLv8ljsqvPVVPue6yGJ39fl9hDL6STQxcXwvHZqiG"
INFLUXDB_ORG = "stadtwerke"
INFLUXDB_BUCKET = "iot_data"

# Kafka-Consumer initialisieren
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'persistence-service',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe([KAFKA_TOPIC])

# InfluxDB-Client initialisieren
idb = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = idb.write_api(write_options=SYNCHRONOUS)


def store_in_influxdb(topic, payload):
    try:
        # Topic den Tags zuweisen
        topics = topic.split("/")
        standort, maschinentyp, maschinen_id, status_type = topics[
            1], topics[2], topics[3], topics[4]

        # Datenpunkt erstellen
        point = (
            idb.Point(status_type)
            .tag("standort", standort)
            .tag("maschinentyp", maschinentyp)
            .tag("maschinen_id", maschinen_id)
            .field("status_code", payload.get("status_code", ""))
            .field("status_text", payload.get("status_text", ""))
            .field("context", payload.get("context", ""))
            .time(payload["timestamp"])
        )

        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        print(f"✅ Nachricht gespeichert: {payload}")
    except Exception as e:
        print(f"❌ Fehler beim Speichern in InfluxDB: {e}")


try:
    print(f"🔄 Warte auf Nachrichten aus Kafka-Topic '{KAFKA_TOPIC}'...")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"❌ Kafka-Fehler: {msg.error()}")
            continue

        topic = msg.topic
        payload = json.loads(msg.value().decode())
        store_in_influxdb(topic, payload)
finally:
    consumer.close()
    idb.close()
