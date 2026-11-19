import random
import time


class SimuladorEstacion:
    def __init__(self):
        self.inicio_ts = time.time()
        self.temp = 24.5
        self.hum = 58.0
        self.pres = 1013.2
        self.aire = 28

        self.umbrales = {"temp": 35.0, "hum": 80.0, "aire": 60}
        self.histeresis = 1.5
        self.intervalo_ms = 2000
        self.silenciado = False
        self.modo_pantalla = "auto"

        self.estado_alerta = False
        self.forzar_pico = False

    def obtener_categoria_aire(self, porcentaje):
        if porcentaje <= 33:
            return "Buena"
        elif porcentaje <= 66:
            return "Moderada"
        return "Mala"

    def generar_lectura(self):
        if self.forzar_pico:
            self.temp = round(self.umbrales["temp"] + 3.5, 1)
            self.aire = min(100, self.umbrales["aire"] + 20)
            self.forzar_pico = False
        else:
            self.temp = round(max(10.0, min(50.0, self.temp + random.uniform(-0.8, 0.8))), 1)
            self.hum = round(max(20.0, min(99.0, self.hum + random.uniform(-1.5, 1.5))), 1)
            self.pres = round(max(980.0, min(1040.0, self.pres + random.uniform(-0.4, 0.4))), 1)
            self.aire = max(0, min(100, self.aire + random.randint(-4, 4)))

        alerta_info = self._evaluar_alarmas()

        return {
            "uptime_s": int(time.time() - self.inicio_ts),
            "temp": self.temp,
            "hum": self.hum,
            "pres": self.pres,
            "aire": self.aire,
            "categoria": self.obtener_categoria_aire(self.aire),
            "alerta": alerta_info["activa"],
            "var_alerta": alerta_info["variable"],
            "val_alerta": alerta_info["valor"],
            "umb_alerta": alerta_info["umbral"],
            "led_verde": not alerta_info["activa"],
            "led_rojo": alerta_info["activa"],
            "buzzer_activo": alerta_info["activa"] and not self.silenciado,
        }

    def _evaluar_alarmas(self):
        t_alerta = self.temp > self.umbrales["temp"]
        h_alerta = self.hum > self.umbrales["hum"]
        a_alerta = self.aire > self.umbrales["aire"]
        detectada = t_alerta or h_alerta or a_alerta

        if self.estado_alerta and not detectada:
            t_ok = self.temp <= (self.umbrales["temp"] - self.histeresis)
            h_ok = self.hum <= (self.umbrales["hum"] - self.histeresis)
            a_ok = self.aire <= (self.umbrales["aire"] - self.histeresis)
            if t_ok and h_ok and a_ok:
                self.estado_alerta = False
        else:
            self.estado_alerta = detectada

        var_nom, var_val, var_umb = "ok", 0, 0
        if t_alerta:
            var_nom, var_val, var_umb = "Temperatura", self.temp, self.umbrales["temp"]
        elif h_alerta:
            var_nom, var_val, var_umb = "Humedad", self.hum, self.umbrales["hum"]
        elif a_alerta:
            var_nom, var_val, var_umb = "Calidad Aire", self.aire, self.umbrales["aire"]

        return {
            "activa": self.estado_alerta,
            "variable": var_nom,
            "valor": var_val,
            "umbral": var_umb,
        }
