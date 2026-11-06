import machine

class GestorAlarmas:
    def __init__(self, pin_verde, pin_rojo, pin_buzzer, umbrales):
        self.led_verde = machine.Pin(pin_verde, machine.Pin.OUT)
        self.led_rojo = machine.Pin(pin_rojo, machine.Pin.OUT)
        self.buzzer = machine.Pin(pin_buzzer, machine.Pin.OUT)
        self.umbrales = umbrales
        self.silenciado = False
        self.estado_alerta = False
        self.histeresis = 1.5

    def evaluar(self, datos):
        temp_alerta = datos.get('temp', 0) > self.umbrales.get('temp', 35)
        hum_alerta = datos.get('hum', 0) > self.umbrales.get('hum', 80)
        aire_alerta = datos.get('aire', 0) > self.umbrales.get('aire', 60)

        alerta_detectada = temp_alerta or hum_alerta or aire_alerta

        if self.estado_alerta and not alerta_detectada:
            temp_ok = datos.get('temp', 0) <= (self.umbrales.get('temp', 35) - self.histeresis)
            hum_ok = datos.get('hum', 0) <= (self.umbrales.get('hum', 80) - self.histeresis)
            aire_ok = datos.get('aire', 0) <= (self.umbrales.get('aire', 60) - self.histeresis)
            if temp_ok and hum_ok and aire_ok:
                self.estado_alerta = False
        else:
            self.estado_alerta = alerta_detectada

        if self.estado_alerta:
            self.led_verde.value(0)
            self.led_rojo.value(1)
            self.buzzer.value(0 if self.silenciado else 1)
        else:
            self.led_verde.value(1)
            self.led_rojo.value(0)
            self.buzzer.value(0)

        var_nom, var_val, var_umb = "ok", 0, 0
        if temp_alerta:
            var_nom, var_val, var_umb = "temp", datos.get('temp', 0), self.umbrales.get('temp', 35)
        elif hum_alerta:
            var_nom, var_val, var_umb = "hum", datos.get('hum', 0), self.umbrales.get('hum', 80)
        elif aire_alerta:
            var_nom, var_val, var_umb = "aire", datos.get('aire', 0), self.umbrales.get('aire', 60)

        return self.estado_alerta, var_nom, var_val, var_umb
