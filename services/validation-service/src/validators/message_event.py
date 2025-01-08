import re
from jsonschema import validate, ValidationError

# JSON-Schema für die Validierung
payload_schema = {
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


class MessageEvent:
    """
    Repräsentiert ein strukturiertes MessageEvent mit validierten Daten. 
    Dieses Objekt wird vom Service nach erfolgreicher Validierung zurückgegeben.
    """

    def __init__(self):
        self.timestamp = None
        self._standort = None
        self._maschinentyp = None
        self._maschinen_id = None
        self._status_type = None
        self._value = None
        self._sensor_id = None

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

    @property
    def standort(self):
        return self._standort

    @standort.setter
    def standort(self, value):
        self._standort = value

    @property
    def maschinentyp(self):
        return self._maschinentyp

    @maschinentyp.setter
    def maschinentyp(self, value):
        self._maschinentyp = value

    @property
    def maschinen_id(self):
        return self._maschinen_id

    @maschinen_id.setter
    def maschinen_id(self, value):
        self._maschinen_id = value

    @property
    def status_type(self):
        return self._status_type

    @status_type.setter
    def status_type(self, value):
        self._status_type = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def sensor_id(self):
        return self._sensor_id

    @sensor_id.setter
    def sensor_id(self, value):
        self._sensor_id = value

    def sanitize_input(self, user_input):
        """
        Überprüft, ob die Eingabe nur erlaubte Zeichen enthält.
        """
        if not re.match("^[a-zA-Z0-9_-]+$", user_input):
            raise ValueError("Ungültige Eingabe")
        return user_input

    def sanitize_field(self, value, field_name, max_length=1000):
        """
        Validiert, ob ein Feld ein gültiger String ist und nicht zu lang ist.
        """
        if not isinstance(value, str):
            raise ValueError(f"{field_name} muss ein String sein.")
        if len(value) > max_length:
            raise ValueError(f"{field_name} ist zu lang.")
        return value

    def is_valid(self):
        """
        Validiert das MessageEvent-Objekt.
        Führt JSON-Schema-Validierung und zusätzliche Prüfungen durch.
        """
        errors = []

        # JSON-Schema-Validierung
        try:
            validate(instance=self.to_dict(), schema=payload_schema)
        except ValidationError as e:
            errors.append(f"Schema-Validierungsfehler: {e.message}")

        # Zusätzliche Prüfungen
        try:
            self.sanitize_input(self.standort)
            self.sanitize_input(self.maschinentyp)
            self.sanitize_input(self.maschinen_id)
            self.sanitize_input(self.sensor_id)
            self.sanitize_field(self.timestamp, "timestamp")
        except ValueError as e:
            errors.append(str(e))

        # Rückgabe der Validierungsergebnisse
        return len(errors) == 0, errors

    def to_dict(self):
        """
        Transformiert eine MessageEvent-Instanz in ein generisches Format
        """
        return {
            "timestamp": self.timestamp,
            "measurement": self.status_type,
            "tags": {
                "standort": self.standort,
                "maschinentyp": self.maschinentyp,
                "maschinen_id": self.maschinen_id,
                "sensor_id": self.sensor_id,
            },
            "data": {
                "value": self.value,
            }
        }
