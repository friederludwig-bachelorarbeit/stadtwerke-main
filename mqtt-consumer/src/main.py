import os
import json
from src.config import get_logger
from paho.mqtt.client import Client
from confluent_kafka import Producer

logger = get_logger()

MQTT_BROKER = os.getenv("MQTT_BROKER", "locahost")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")

MQTT_PORT = 1883
MQTT_TOPIC = "stadtwerke/#"
KAFKA_PRODUCER_TOPIC = "raw-messages"

kafka_producer = Producer({'bootstrap.servers': KAFKA_BROKER})


def on_message(client, userdata, message):
    """
    Callback Funktion für eingehende MQTT-Nachrichten.
    """
    try:
        topic = message.topic
        payload = json.loads(message.payload.decode())
        payload['mqtt_topic'] = topic

        # Nachricht an Kafka senden
        try:
            kafka_producer.produce(
                KAFKA_PRODUCER_TOPIC,
                key=topic,
                value=json.dumps(payload)
            )
            kafka_producer.flush()
            logger.info(
                f"Nachricht an Kafka gesendet: {payload} | Kafka Topic: {KAFKA_PRODUCER_TOPIC}")
        except Exception as e:
            logger.error(f"Fehler beim Senden an Kafka: {e}")

    except json.JSONDecodeError:
        logger.error("Nachricht ist kein gültiges JSON.")
    except Exception as e:
        logger.error(f"Ein Fehler ist aufgetreten: {e}")


if __name__ == "__main__":
    # MQTT-Client konfigurieren
    mqtt_client = Client()
    mqtt_client.on_message = on_message

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
