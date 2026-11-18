from ssd1306 import SSD1306_I2C

class PantallaOLED:
    def __init__(self, i2c, width=128, height=64, addr=0x3C):
        self.oled = SSD1306_I2C(width, height, i2c, addr=addr)
        self.pagina_actual = 0
        self.modo_auto = True

    def set_modo_pantalla(self, modo):
        if modo == "auto":
            self.modo_auto = True
        else:
            self.modo_auto = False
            self.pagina_actual = int(modo) % 4

    def rotar_pagina(self):
        if self.modo_auto:
            self.pagina_actual = (self.pagina_actual + 1) % 4

    def actualizar(self, datos, red_info):
        self.oled.fill(0)
        p = self.pagina_actual
        
        if p == 0:
            self.oled.text("=== TEMP / HUM ===", 0, 0)
            self.oled.text("Temp: {:.1f} C".format(datos.get('temp', 0.0)), 0, 22)
            self.oled.text("Hum:  {:.1f} %".format(datos.get('hum', 0.0)), 0, 42)
        elif p == 1:
            self.oled.text("=== PRESION ===", 0, 0)
            self.oled.text("Pres: {:.1f}".format(datos.get('pres', 1013.2)), 0, 25)
            self.oled.text("      hPa", 0, 40)
        elif p == 2:
            self.oled.text("=== CALIDAD AIRE ===", 0, 0)
            aire = datos.get('aire', 0)
            cat = datos.get('categoria', 'N/A')
            self.oled.text("Aire: {}% ({})".format(aire, cat[:5]), 0, 20)
            self.oled.rect(0, 45, 128, 14, 1)
            ancho = int((aire / 100.0) * 124)
            if ancho > 0:
                self.oled.fill_rect(2, 47, ancho, 10, 1)
        elif p == 3:
            self.oled.text("=== ESTADO RED ===", 0, 0)
            self.oled.text("WiFi: " + ("OK" if red_info.get('wifi') else "DISC"), 0, 18)
            self.oled.text("MQTT: " + ("OK" if red_info.get('mqtt') else "DISC"), 0, 34)
            self.oled.text("IP: " + red_info.get('ip', '0.0.0.0')[:15], 0, 50)
            
        self.oled.show()
