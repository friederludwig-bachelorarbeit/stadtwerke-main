import re
from abc import ABC, abstractmethod
from datetime import datetime
from message_event import MessageEvent


class ProtocolMessageValidator(ABC):
    """
    Abstrakte Basisklasse für Protokoll-Validatoren.
    """
    @abstractmethod
    def validate(self, payload):
        """
        Validiert den Payload für ein spezifisches Protokoll.
        """
        pass

    def sanitize_input(self, value):
        """
        Validiert den Wert eines Feldes.
        :param value: Der zu überprüfende Wert.
        :return: Der validierte Wert.
        """
        valid_types = str, int, float
        max_str_length = 1000

        regex = re.compile("^[a-zA-Z0-9_:,;\\- '\"()]+$")

        if isinstance(value, str):
            if not re.match(regex, value):
                raise ValueError(f"{'Eingabe'} enthält ungültige Zeichen.")
            if len(value) > max_str_length:
                raise ValueError(f"{'Eingabe'} ist zu lang (max. {max_str_length} Zeichen).")
        elif not isinstance(value, (valid_types)):
            raise ValueError(f"{'Eingabe'} hat einen ungültigen Typ ({type(value).__name__}).")

        return value

    def validate_timestamp(self, timestamp):
        """
        Validiert Zeitstempel: ISO 8601-Format 
        :param timestamp: Der zu prüfende Zeitstempel.
        :return: True, wenn der Zeitstempel gültig ist.
        :raises ValueError: Wenn der Zeitstempel ungültig ist.
        """
        try:
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            return True
        except ValueError as e:
            raise ValueError(f"Ungültiger Zeitstempel: {timestamp}. Fehler: {str(e)}")

    def validate_message_event(self, event: MessageEvent):
        """
        Führt die Validierung eines MessageEvent-Objekts durch.
        :param event: Instanz MessageEvent-Objekt.
        :return: Tuple (is_valid: bool, errors: list)
        """
        errors = []
        try:
            self.validate_timestamp(event.timestamp)
            self.sanitize_input(event.standort)
            self.sanitize_input(event.maschinentyp)
            self.sanitize_input(event.maschinen_id)
            self.sanitize_input(event.sensor_id)
            self.sanitize_input(event.value)
        except ValueError as e:
            errors.append(str(e))

        return len(errors) == 0, errors
