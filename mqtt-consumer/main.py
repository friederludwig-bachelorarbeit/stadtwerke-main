import json
from paho.mqtt.client import Client
from confluent_kafka import Producer, KafkaException

MQTT_BROKER = "mqtt-broker"
MQTT_PORT = 1883
MQTT_TOPIC = "stadtwerke/#"
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "raw-messages"

MQTT_BROKER = "localhost"  # Wenn Anwenung mit venv gestartet
KAFKA_BROKER = "localhost:9092"  # Wenn Anwenung mit venv gestartet

# Kafka-Producer initialisieren (optional, falls Kafka konfiguriert ist)
kafka_producer = None
if KAFKA_BROKER:
    try:
        kafka_producer = Producer({'bootstrap.servers': KAFKA_BROKER})
        print(f"✅ Verbunden mit Kafka-Broker: {KAFKA_BROKER}")
    except KafkaException as e:
        print(f"❌ Fehler bei der Verbindung mit Kafka: {e}")
        kafka_producer = None


def on_message(client, userdata, message):
    """
    Callback Funktion für eingehende MQTT-Nachrichten.
    """
    try:
        topic = message.topic
        payload = json.loads(message.payload.decode())
        payload['topic'] = topic
        print(f"Eingehende Nachricht von {topic}: {payload}")

        # Nachricht an Kafka senden, falls konfiguriert
        try:
            kafka_producer.produce(
                KAFKA_TOPIC,
                key=topic,
                value=json.dumps(payload)
            )
            kafka_producer.flush()
            print(f"✅ Nachricht an Kafka gesendet: {payload}")
        except Exception as e:
            print(f"❌ Fehler beim Senden an Kafka: {e}")

    except json.JSONDecodeError:
        print("❌ Nachricht ist kein gültiges JSON.")
    except Exception as e:
        print(f"❌ Ein Fehler ist aufgetreten: {e}")


# MQTT-Client konfigurieren
mqtt_client = Client()
mqtt_client.on_message = on_message
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.subscribe(MQTT_TOPIC)
    print(f"✅ Verbunden mit MQTT-Broker {MQTT_BROKER}:{MQTT_PORT}")
    mqtt_client.loop_forever()
except Exception as e:
    print(f"❌ Fehler bei der Verbindung mit MQTT-Broker: {e}")
