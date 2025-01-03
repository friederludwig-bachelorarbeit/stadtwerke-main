import re
from config import get_logger
from jsonschema import validate, ValidationError

OFFSET_FILE = "last_offset.json"

logger = get_logger()

# JSON-Schema für die Nachrichten
message_schema = {
    "type": "object",
    "properties": {
        "timestamp": {
            "type": "string",
            "format": "date-time"
        },
        "value": {
            "anyOf": [
                {"type": "integer"},
                {"type": "string"}
            ]
        },
    },
    "required": ["timestamp"],
    "additionalProperties": True
}


def sanitize_input(user_input):
    """
    Überprüft, ob die Eingabe nur erlaubte Zeichen enthält.
    """
    if not re.match("^[a-zA-Z0-9_-]+$", user_input):
        raise ValueError("Ungültige Eingabe")
    return user_input


def sanitize_field(value, field_name, max_length=1000):
    """
    Validiert, ob ein Feld ein gültiger String ist und nicht zu lang ist.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} muss ein String sein.")
    if len(value) > max_length:
        raise ValueError(f"{field_name} ist zu lang.")
    return value


def validate_message_with_schema(payload):
    """
    Validiert eine Nachricht basierend auf dem JSON-Schema.
    """
    try:
        validate(instance=payload, schema=message_schema)
        return True, "Nachricht ist gültig."
    except ValidationError as e:
        return False, f"Schema-Validierungsfehler: {e.message}"


def get_mqtt_topic_segment(mqtt_topics, index, default=None):
    """
    Versucht, ein Segment aus dem MQTT-Topic zu holen. 
    Gibt default zurück, falls Index out of range.
    """
    try:
        return mqtt_topics[index]
    except IndexError:
        return default


def on_assign(consumer, partitions):
    logger.info(f"Partitions assigned: {partitions}")
    consumer.assign(partitions)


def on_revoke(consumer, partitions):
    try:
        # Prüfe, ob es Partitionen gibt, die einen gültigen Offset haben (-1001 = kein Offset)
        partitions_to_commit = [p for p in partitions if p.offset != -1001]
        if partitions_to_commit:
            consumer.commit(asynchronous=False)
            logger.info(f"Partitions revoked: {partitions}")
    except Exception as e:
        logger.error(f"Fehler beim Commit vor Revoke: {e}")
