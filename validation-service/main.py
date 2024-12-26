import json
from confluent_kafka import Consumer, Producer
from utils import validate_message_with_schema

# Kafka-Konfiguration
# KAFKA_BROKER = "kafka:9092"
RAW_TOPIC = "raw-messages"
VALIDATED_TOPIC = "validated-messages"
ERROR_TOPIC = "error-messages"

KAFKA_BROKER = "localhost:9092"  # Wenn Anwenung mit venv gestartet

# Kafka-Consumer und Producer konfigurieren
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'validation-service',
    'auto.offset.reset': 'earliest'
})

producer = Producer({'bootstrap.servers': KAFKA_BROKER})


def process_messages():
    """
    Konsumiert Nachrichten aus Kafka, validiert sie und sendet validierte oder fehlerhafte Nachrichten
    an die entsprechenden Topics.
    """
    consumer.subscribe([RAW_TOPIC])

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Kafka-Fehler: {msg.error()}")
            continue

        try:
            payload = json.loads(msg.value().decode('utf-8'))
            print(f"Empfangene Nachricht: {payload}")

            is_valid, message = validate_message_with_schema(payload)
            if is_valid:
                producer.produce(VALIDATED_TOPIC, json.dumps(
                    payload).encode('utf-8'))
                producer.flush()
                print(
                    f"Validierte Nachricht an {VALIDATED_TOPIC} gesendet: {payload}")
            else:
                error_payload = {
                    "original_message": payload,
                    "error": message
                }
                producer.produce(ERROR_TOPIC, json.dumps(
                    error_payload).encode('utf-8'))
                producer.flush()
                print(
                    f"Fehlerhafte Nachricht an {ERROR_TOPIC} gesendet: {error_payload}")
        except json.JSONDecodeError:
            print("Ungültiges JSON-Format in der empfangenen Nachricht.")
        except Exception as e:
            print(f"Unerwarteter Fehler: {e}")


if __name__ == "__main__":
    print("Validation Service gestartet.")
    try:
        process_messages()
    except KeyboardInterrupt:
        print("Validation Service beendet.")
    finally:
        consumer.close()
