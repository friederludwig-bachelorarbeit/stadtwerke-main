import os
import json
from src.config import get_logger
from confluent_kafka import Consumer
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

logger = get_logger()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "locahost:9092")
KAFKA_CONSUMER_TOPIC = "validated-messages"
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv(
    "INFLUXDB_TOKEN", "O96o2El4fFg_oYpT1xbtyOz1HII-asOmsy-aRVwoO-Z2QRbS11KCjRK-_klydrfPhSDQeLhrQpd8WWzOnrNk2g==")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "stadtwerke")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_ORG", "iot_data")

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'persistence-service',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe([KAFKA_CONSUMER_TOPIC])

influxdb_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
influxdb_write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)


def store_in_influxdb(payload):
    try:
        # Topic den Tags zuweisen
        topics = payload["mqtt_topic"].split("/")
        standort, maschinentyp, maschinen_id, status_type = topics[
            1], topics[2], topics[3], topics[4]

        # Datenpunkt erstellen
        point = (
            Point(status_type)
            .tag("standort", standort)
            .tag("maschinentyp", maschinentyp)
            .tag("maschinen_id", maschinen_id)
            .field("status_code", payload.get("status_code", ""))
            .field("status_text", payload.get("status_text", ""))
            .field("context", payload.get("context", ""))
            .time(payload["timestamp"])
        )
        influxdb_write_api.write(bucket=INFLUXDB_BUCKET, record=point)

        logger.info(f"Nachricht gespeichert: {payload}")
    except Exception as e:
        logger.error(f"Fehler beim Speichern in InfluxDB: {e}")


try:
    logger.info("Persistence Service gestartet.")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            # logger.error(f"Kafka-Fehler: {msg.error()}")
            continue

        payload = json.loads(msg.value().decode())
        store_in_influxdb(payload)
except KeyboardInterrupt:
    consumer.close()
    influxdb_client.close()
finally:
    consumer.close()
    influxdb_client.close()
