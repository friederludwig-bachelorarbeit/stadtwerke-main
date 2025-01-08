from abc import ABC, abstractmethod
from jsonschema import validate, ValidationError


class ProtocolMessageValidator(ABC):
    """
    Abstrakte Basisklasse für Protokoll-Validatoren.
    """

    def __call__(self, payload):
        return self.validate(payload)

    @abstractmethod
    def validate(self, payload):
        """
        Validiert den Payload für ein spezifisches Protokoll.
        """
        pass

    def validate_json_with_schema(self, payload, schema):
        """
        Führt die JSON-Schema-Validierung durch.
        :param payload: Zu validierende Nachricht.
        :param schema: JSON-Schema für die Validierung.
        :return: Tuple (is_valid: bool, error_message: str)
        """
        try:
            validate(instance=payload, schema=schema)
            return True, None
        except ValidationError as e:
            return False, f"Schema-Validierungsfehler: {e.message}"
