# Estación de Monitoreo Ambiental con ESP32 (MicroPython)

**Asignatura:** Programación II  
**Programa:** Ingeniería Electrónica - Universidad Tecnológica de Pereira (UTP)[cite: 2]  
**Integrantes:** Claudio Tovar Tovar & Juan Esteban Gómez Loaiza[cite: 2]  

---

## Descripción del Proyecto
Este desarrollo corresponde a la entrega del **Parcial 2**. Se trata del firmware en MicroPython para una estación de monitoreo ambiental que mide temperatura, humedad, presión barométrica e índice de calidad del aire[cite: 2]. Los datos se presentan de forma local en una pantalla OLED SSD1306 y se transmiten vía Wi-Fi mediante el protocolo MQTT a un broker público[cite: 2, 3].

---

## Arquitectura de Archivos (POO)

* **`config.py`**: Parámetros globales, constantes de red, broker y asignación de pines GPIO[cite: 13].
* **`sensores.py`**: Clases orientadas a objetos (`SensorDHT22`, `SensorBMP180`, `SensorAnalogico`) derivadas de la clase base `Sensor`.
* **`pantalla.py`**: Control de la pantalla OLED SSD1306 con páginas de visualización rotativas[cite: 9].
* **`alarmas.py`**: Lógica de evaluación de umbrales con histéresis y control del LED Verde, LED Rojo y Buzzer[cite: 10].
* **`red_mqtt.py`**: Manejo de la conexión Wi-Fi, cliente MQTT, envío de telemetría, alertas y recepción de comandos[cite: 11].
* **`main.py`**: Ciclo principal no bloqueante gestionado por marcas de tiempo con `time.ticks_ms()`.

---

## Asignación de Pines del ESP32

| Componente | Pin GPIO / Bus | Descripción |
| :--- | :--- | :--- |
| **DHT22** | GPIO 15 | Sensor de Temperatura y Humedad[cite: 3]. |
| **Potenciómetro (MQ-2)** | GPIO 34 | ADC1 (Simulación Calidad del Aire 0-100%)[cite: 3]. |
| **BMP180** | I2C (SDA 21 / SCL 22) | Sensor de Presión Barométrica (Dirección `0x77`)[cite: 3]. |
| **OLED SSD1306** | I2C (SDA 21 / SCL 22) | Pantalla visualizadora (Dirección `0x3C`)[cite: 3]. |
| **LED Verde** | GPIO 26 | Estado Normal del sistema[cite: 3, 13]. |
| **LED Rojo** | GPIO 27 | Estado de Alerta activo[cite: 3, 13]. |
| **Buzzer** | GPIO 25 | Alarma sonora local[cite: 3, 13]. |

---

## Tópicos MQTT (`pro2/estacion01/`)

* **`telemetria`**: Lecturas consolidadas de sensores (JSON, QoS 0).
* **`estado`**: Estado de conexión `online`/`offline` mediante *Last Will and Testament* (QoS 1, Retain).
* **`alertas`**: Eventos generados al superar o retornar de un umbral (JSON, QoS 1)[cite: 4].
* **`config`**: Configuración activa del dispositivo (JSON, QoS 1, Retain)[cite: 4].
* **`cmd/#`**: Tópicos de suscripción para comandos remotos (`cmd/intervalo`, `cmd/umbrales`, `cmd/silencio`, `cmd/pantalla`)[cite: 4].

---

## 🔗 Simulación Interactiva
**[Acceder a la simulación en Wokwi](https://wokwi.com/projects/479954901774540801)**
