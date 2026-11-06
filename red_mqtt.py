import network
import json
import time
from umqtt.simple import MQTTClient

class ClienteMQTT:
    def __init__(self, prefix, broker, port, callback_cmd):
        self.prefix = prefix
        self.broker = broker
        self.port = port
        self.callback_cmd = callback_cmd
        self.client = None
        self.wlan = network.WLAN(network.STA_IF)
        self.ip = "0.0.0.0"
        self.conectado_mqtt = False

    def conectar_wifi(self, ssid="Wokwi-GUEST", password=""):
        self.wlan.active(True)
        if not self.wlan.isconnected():
            self.wlan.connect(ssid, password)
            timeout = 10
            while not self.wlan.isconnected() and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5
        if self.wlan.isconnected():
            self.ip = self.wlan.ifconfig()[0]
            return True
        return False

    def conectar_mqtt(self):
        try:
            client_id = "esp32_estacion_" + str(time.ticks_ms())
            self.client = MQTTClient(client_id, self.broker, port=self.port)
            topico_estado = self.prefix + "estado"
            self.client.set_last_will(topico_estado, "offline", retain=True, qos=1)
            self.client.set_callback(self.callback_cmd)
            self.client.connect()
            self.client.subscribe(self.prefix + "cmd/#")
            self.client.publish(topico_estado, "online", retain=True, qos=1)
            self.conectado_mqtt = True
            return True
        except Exception:
            self.conectado_mqtt = False
            return False

    def verificar_mensajes(self):
        if self.conectado_mqtt and self.client:
            try:
                self.client.check_msg()
            except Exception:
                self.conectado_mqtt = False

    def publicar(self, subtopico, payload, retain=False, qos=0):
        if self.conectado_mqtt and self.client:
            try:
                topico = self.prefix + subtopico
                if isinstance(payload, dict):
                    payload = json.dumps(payload)
                self.client.publish(topico, payload, retain=retain, qos=qos)
            except Exception:
                self.conectado_mqtt = False
