import re
from jsonschema import validate, ValidationError

# JSON-Schema für die Nachrichten
message_schema = {
    "type": "object",
    "properties": {
        "timestamp": {"type": "string", "format": "date-time"},
        "status_code": {"type": "integer"},
        "status_text": {"type": "string"},
        "context": {"type": "string"}
    },
    "required": ["timestamp", "status_text"],
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
