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
        self._measurement = None
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
    def measurement(self):
        return self._measurement

    @measurement.setter
    def measurement(self, value):
        self._measurement = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = self.convert_to_appropriate_type(value)

    @property
    def sensor_id(self):
        return self._sensor_id

    @sensor_id.setter
    def sensor_id(self, value):
        self._sensor_id = value

    def convert_to_appropriate_type(self, value):
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return str(value)

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "measurement": self.measurement,
            "tags": {
                "standort": self.standort,
                "maschinentyp": self.maschinentyp,
                "maschinen_id": self.maschinen_id,
                "sensor_id": self.sensor_id,
            },
            "fields": {
                "value": self.value,
            }
        }
