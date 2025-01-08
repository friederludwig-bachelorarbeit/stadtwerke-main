from validators.mqtt_validator import MQTTMessageValidator
from validators.http_validator import HTTPMessageValidator


class ValidatorFactory:
    @staticmethod
    def get_validator(protocol_type):
        if protocol_type == "mqtt":
            return MQTTMessageValidator()
        elif protocol_type == "http":
            return HTTPMessageValidator()
        else:
            return None
