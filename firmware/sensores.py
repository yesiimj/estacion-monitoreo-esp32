import machine
import dht

class Sensor:
    def iniciar(self):
        raise NotImplementedError("Debes implementar iniciar()")

    def leer(self):
        raise NotImplementedError("Debes implementar leer()")

    def valor(self):
        raise NotImplementedError("Debes implementar valor()")

    def es_valido(self):
        raise NotImplementedError("Debes implementar es_valido()")

class SensorDHT22(Sensor):
    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.sensor = None
        self.temp = 0.0
        self.hum = 0.0
        self.valido = False

    def iniciar(self):
        try:
            self.sensor = dht.DHT22(machine.Pin(self.pin_num))
            self.valido = True
        except Exception:
            self.valido = False

    def leer(self):
        if not self.sensor:
            self.iniciar()
        try:
            self.sensor.measure()
            self.temp = round(self.sensor.temperature(), 1)
            self.hum = round(self.sensor.humidity(), 1)
            self.valido = True
        except OSError:
            self.valido = False
        return self.valido

    def valor(self):
        return {"temp": self.temp, "hum": self.hum}

    def es_valido(self):
        return self.valido

class SensorAnalogico(Sensor):
    def __init__(self, pin_num):
        self.adc = machine.ADC(machine.Pin(pin_num))
        self.adc.atten(machine.ADC.ATTN_11DB)
        self.porcentaje = 0
        self.valido = False

    def iniciar(self):
        self.valido = True

    def leer(self):
        try:
            muestras = [self.adc.read() for _ in range(10)]
            promedio = sum(muestras) / len(muestras)
            self.porcentaje = int((promedio / 4095.0) * 100)
            self.valido = True
        except Exception:
            self.valido = False
        return self.valido

    def valor(self):
        return self.porcentaje

    def es_valido(self):
        return self.valido

class SensorBMP180(Sensor):
    def __init__(self, i2c, addr=0x77):
        self.i2c = i2c
        self.addr = addr
        self.presion = 1013.2
        self.valido = False

    def iniciar(self):
        self.valido = True

    def leer(self):
        self.presion = 1013.2
        self.valido = True
        return self.valido

    def valor(self):
        return self.presion

    def es_valido(self):
        return self.valido
