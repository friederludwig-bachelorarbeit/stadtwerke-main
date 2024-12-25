import os
import json
from confluent_kafka import Consumer
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Konfiguration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "validated-messages")

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv(
    "INFLUXDB_TOKEN", "DF1TBbibSo5P3FC5c5buuaPfLv8ljsqvPVVPue6yGJ39fl9hDL6STQxcXwvHZqiG")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "stadtwerke")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "iot_data")

# Kafka-Consumer initialisieren
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'persistence-service',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe([KAFKA_TOPIC])

# InfluxDB-Client initialisieren
influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# Nachrichten verarbeiten


def store_in_influxdb(payload):
    try:
        point = Point("sensor_data") \
            .tag("location", payload.get("location", "unknown")) \
            .field("temperature", payload["temperature"]) \
            .field("humidity", payload["humidity"]) \
            .time(payload.get("timestamp", None))

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

        payload = json.loads(msg.value().decode())
        store_in_influxdb(payload)
finally:
    consumer.close()
    influx_client.close()
