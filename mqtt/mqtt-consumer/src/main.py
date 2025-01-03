import os
import json
from contextlib import contextmanager
from src.config import get_logger
from paho.mqtt.client import Client
from confluent_kafka import Producer

logger = get_logger()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "stadtwerke/#")
KAFKA_PRODUCER_TOPIC = os.getenv("KAFKA_PRODUCER_TOPIC", "raw-messages")


@contextmanager
def kafka_producer():
    """ Kontextmanager für den Kafka-Producer."""
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
    try:
        yield producer
    finally:
        producer.flush()


def on_message(client, userdata, message, producer):
    """
    Callback-Funktion für eingehende MQTT-Nachrichten.
    Sendet die Nachricht an Kafka.
    """
    try:
        topic = message.topic
        payload = json.loads(message.payload.decode())
        payload['mqtt_topic'] = topic

        # Nachricht an Kafka senden
        producer.produce(
            KAFKA_PRODUCER_TOPIC,
            key=topic,
            value=json.dumps(payload)
        )
        logger.info(
            f"Nachricht an Kafka gesendet: {payload}"
        )
    except json.JSONDecodeError:
        logger.error("Nachricht ist kein gültiges JSON.")
    except Exception as e:
        logger.error(f"Fehler beim Verarbeiten der Nachricht: {e}")


if __name__ == "__main__":
    mqtt_client = Client()

    with kafka_producer() as producer:
        def wrapped_on_message(client, userdata, message):
            on_message(client, userdata, message, producer)

        mqtt_client.on_message = wrapped_on_message

        try:
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
            mqtt_client.subscribe(MQTT_TOPIC)
            logger.info(f"Verbunden mit MQTT-Broker {MQTT_BROKER}:{MQTT_PORT}")
            mqtt_client.loop_forever()
        except KeyboardInterrupt:
            mqtt_client.disconnect()
        except Exception as e:
            logger.error(f"Fehler bei der Verbindung mit MQTT-Broker: {e}")
            mqtt_client.disconnect()
