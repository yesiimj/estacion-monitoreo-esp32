import machine
import time
import json

from config import *
from sensores import SensorDHT22, SensorAnalogico, SensorBMP180
from pantalla import PantallaOLED
from alarmas import GestorAlarmas
from red_mqtt import ClienteMQTT

class Estacion:
    def __init__(self):
        self.i2c = machine.I2C(0, sda=machine.Pin(PIN_I2C_SDA), scl=machine.Pin(PIN_I2C_SCL))
        self.dht = SensorDHT22(PIN_DHT)
        self.pot = SensorAnalogico(PIN_POT_AIRE)
        self.bmp = SensorBMP180(self.i2c, addr=I2C_ADDR_BMP180)
        self.oled = PantallaOLED(self.i2c, addr=I2C_ADDR_OLED)
        
        self.umbrales = {"temp": 35, "hum": 80, "aire": 60}
        self.alarmas = GestorAlarmas(PIN_LED_VERDE, PIN_LED_ROJO, PIN_BUZZER, self.umbrales)
        self.red = ClienteMQTT(MQTT_PREFIX, MQTT_BROKER, MQTT_PORT, self._procesar_comando)
        
        self.intervalo_ms = 2000
        self.start_time = time.time()
        self.ultima_lectura = {}
        self.estado_alerta_previo = False

    def iniciar(self):
        self.dht.iniciar()
        self.pot.iniciar()
        self.bmp.iniciar()
        if self.red.conectar_wifi():
            if self.red.conectar_mqtt():
                self._publicar_config()

    def _clasificar_aire(self, porcentaje):
        if porcentaje < 30: return "Buena"
        if porcentaje < 60: return "Moderada"
        return "Mala"

    def _procesar_comando(self, topic, msg):
        try:
            topico_str = topic.decode('utf-8')
            msg_str = msg.decode('utf-8')
            
            if "cmd/intervalo" in topico_str:
                val = int(msg_str)
                if 2000 <= val <= 10000:
                    self.intervalo_ms = val
            elif "cmd/umbrales" in topico_str:
                nuevos_u = json.loads(msg_str)
                self.umbrales.update(nuevos_u)
                self.alarmas.umbrales = self.umbrales
            elif "cmd/silencio" in topico_str:
                self.alarmas.silenciado = (msg_str == "1" or msg_str.lower() == "true")
            elif "cmd/pantalla" in topico_str:
                self.oled.set_modo_pantalla(msg_str)
                
            self._publicar_config()
        except Exception as e:
            print("Error comando:", e)

    def _publicar_config(self):
        payload = {
            "intervalo_ms": self.intervalo_ms,
            "umbral_temp": self.umbrales.get("temp", 35),
            "umbral_hum": self.umbrales.get("hum", 80),
            "umbral_aire": self.umbrales.get("aire", 60),
            "silencio": self.alarmas.silenciado,
            "pantalla": "auto" if self.oled.modo_auto else str(self.oled.pagina_actual)
        }
        self.red.publicar("config", payload, retain=True, qos=1)

    def ejecutar_ciclo(self):
        t_sensor = time.ticks_ms()
        t_refresco = time.ticks_ms()
        t_rotacion = time.ticks_ms()
        
        while True:
            ahora = time.ticks_ms()
            
            # 1. Tarea Muestreo de Sensores
            if time.ticks_diff(ahora, t_sensor) >= self.intervalo_ms:
                t_sensor = ahora
                self.dht.leer()
                self.pot.leer()
                self.bmp.leer()
                
                v_dht = self.dht.valor()
                v_pot = self.pot.valor()
                v_bmp = self.bmp.valor()
                
                self.ultima_lectura = {
                    "uptime_s": time.time() - self.start_time,
                    "temp": v_dht["temp"],
                    "hum": v_dht["hum"],
                    "pres": v_bmp,
                    "aire": v_pot,
                    "categoria": self._clasificar_aire(v_pot)
                }
                
                alerta, var, val, umbral = self.alarmas.evaluar(self.ultima_lectura)
                
                if alerta != self.estado_alerta_previo:
                    payload_alerta = {
                        "variable": var if alerta else "normal",
                        "valor": val if alerta else 0,
                        "umbral": umbral if alerta else 0,
                        "estado": "ALERTA" if alerta else "NORMAL"
                    }
                    self.red.publicar("alertas", payload_alerta, qos=1)
                    self.estado_alerta_previo = alerta

                self.red.publicar("telemetria", self.ultima_lectura, qos=0)

            # 2. Refresco de Pantalla (~500 ms)
            if time.ticks_diff(ahora, t_refresco) >= 500:
                t_refresco = ahora
                info_red = {
                    "wifi": self.red.wlan.isconnected(),
                    "mqtt": self.red.conectado_mqtt,
                    "ip": self.red.ip
                }
                self.oled.actualizar(self.ultima_lectura, info_red)

            # 3. Rotación de Páginas OLED (3000 ms)
            if time.ticks_diff(ahora, t_rotacion) >= 3000:
                t_rotacion = ahora
                self.oled.rotar_pagina()

            # 4. Procesamiento no bloqueante de MQTT
            self.red.verificar_mensajes()

if __name__ == "__main__":
    estacion = Estacion()
    estacion.iniciar()
    estacion.ejecutar_ciclo()
