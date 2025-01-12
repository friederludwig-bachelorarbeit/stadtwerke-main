from validators.base import ProtocolMessageValidator
from message_event import MessageEvent


class MQTTMessageValidator(ProtocolMessageValidator):
    """
    Validator für MQTT-Nachrichten.
    """

    def validate(self, payload):
        """
        Validiert den MQTT-Payload und erstellt ein MessageEvent-Objekt.
        :param payload: Die MQTT-Message (Dictionary).
        :return: MessageEvent-Objekt, wenn die Nachricht gültig ist.
        :raises ValueError: Wenn die Nachricht ungültig ist.
        """
        try:
            # MQTT-Topic in Segmente aufteilen
            mqtt_topics = payload["mqtt_topic"].split("/")

            # MessageEvent erstellen und Felder setzen
            msg = MessageEvent()
            msg.standort = mqtt_topics[1]
            msg.maschinentyp = mqtt_topics[2]
            msg.maschinen_id = mqtt_topics[3]
            msg.measurement = mqtt_topics[4]
            msg.sensor_id = mqtt_topics[5]
            msg.timestamp = payload.get("timestamp")
            msg.value = payload.get("value")

            # Validierung des MessageEvent-Objekts
            msg_is_valid, errors = self.validate_message_event(msg)
            if not msg_is_valid:
                error_msg = f"MessageEvent-Fehler: {', '.join(errors)}"
                raise ValueError(error_msg)

            return msg.to_dict()

        except IndexError as e:
            raise IndexError(f"IndexError: {e} - mqtt_topic enthält nicht genügend Segmente.")

        except KeyError as e:
            raise ValueError(f"Fehlendes erforderliches Feld im Payload: {e}")

        except Exception as e:
            raise ValueError(f"Fehler beim Verarbeiten der MQTT-Nachricht: {e}")
