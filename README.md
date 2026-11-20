# Estación de Monitoreo Ambiental con ESP32

**Asignatura:** Programación II  
**Programa:** Ingeniería Electrónica - Universidad Tecnológica de Pereira (UTP)  
**Integrantes:** Claudio Tovar Tovar & Juan Esteban Gómez Loaiza  

---

## Descripción del Proyecto
Sistema integral de monitoreo ambiental basado en una estación IoT con microcontrolador **ESP32** y una aplicación de escritorio en **Python**. El proyecto se desarrolla de forma incremental:

- **Parcial 2 (Firmware en MicroPython):** Adquisición de variables ambientales (temperatura, humedad, presión barométrica e índice de calidad del aire), visualización local en pantalla OLED SSD1306, gestión de alarmas con histéresis y comunicación vía Wi-Fi mediante protocolo MQTT.
- **Parcial 3 (Interfaz Gráfica de Escritorio):** Aplicación desarrollada con `Tkinter` y Programación Orientada a Objetos (POO) para la visualización en tiempo real de variables, control de parámetros, alarmas visuales e historial de eventos. Actualmente opera con un módulo de datos simulados desacoplado, listo para su futura integración directa vía MQTT con la ESP32.

---

## Estructura del Repositorio

```text
estacion-monitoreo-esp32/
├── firmware/                 # Código en MicroPython para la ESP32 (Parcial 2)
│   ├── alarmas.py
│   ├── config.py
│   ├── diagram.json
│   ├── main.py
│   ├── pantalla.py
│   ├── red_mqtt.py
│   ├── sensores.py
│   └── ssd1306.py
├── interfaz/                 # Aplicación gráfica de escritorio en Python (Parcial 3)
│   ├── app.py
│   ├── componentes.py
│   ├── main.py
│   └── simulador.py
└── README.md
```

---

## 1. Interfaz Gráfica (`interfaz/`)

Desarrollada bajo el paradigma de **Programación Orientada a Objetos (POO)** utilizando la biblioteca estándar `tkinter` y `tkinter.ttk`.

### Arquitectura de Módulos
- **`simulador.py`**: Clase `SimuladorEstacion` que modela las variaciones de los sensores y replica exactamente la lógica de umbrales e histéresis (`1.5` unidades) del firmware.
- **`componentes.py`**: Widgets compuestos reutilizables heredados de `ttk.LabelFrame`:
  - `PanelSensores`: Lecturas en tiempo real, barras de progreso (`Progressbar`) e indicadores visuales de LED Verde, LED Rojo y Buzzer.
  - `PanelControl`: Formulario con validación de datos para umbrales (`Entry`), listas desplegables (`Combobox`) para frecuencia de muestreo y página OLED, y botones de control (`Silenciar Buzzer`, `Pausar`, `Simular Alerta`).
  - `PanelHistorial`: Tabla interactiva (`Treeview`) con barra de desplazamiento y vista de detalle mediante evento de doble clic (`<Double-1>`).
- **`app.py`**: Clase `InterfazEstacion` (`tk.Tk`) que gestiona la ventana principal, el banner global de alarmas y el ciclo periódico no bloqueante mediante `.after()`.
- **`main.py`**: Punto de entrada para ejecutar la aplicación gráfica.

### Ejecución Local de la Interfaz
Requiere Python 3.8 o superior (no requiere dependencias externas):

```bash
cd interfaz
python main.py
```

---

## 2. Firmware ESP32 (`firmware/`)

### Arquitectura de Archivos (POO)
- **`config.py`**: Parámetros globales, constantes de red, broker y asignación de pines GPIO.
- **`sensores.py`**: Clases orientadas a objetos (`SensorDHT22`, `SensorBMP180`, `SensorAnalogico`) derivadas de la clase base `Sensor`.
- **`pantalla.py`**: Control de la pantalla OLED SSD1306 con 4 páginas de visualización rotativas.
- **`alarmas.py`**: Lógica de evaluación de umbrales con histéresis y control del LED Verde, LED Rojo y Buzzer.
- **`red_mqtt.py`**: Manejo de la conexión Wi-Fi, cliente MQTT, envío de telemetría, alertas y recepción de comandos.
- **`main.py`**: Ciclo principal no bloqueante gestionado por marcas de tiempo con `time.ticks_ms()`.

### Asignación de Pines del ESP32

| Componente | Pin GPIO / Bus | Descripción |
| :--- | :--- | :--- |
| **DHT22** | GPIO 15 | Sensor de Temperatura y Humedad. |
| **Potenciómetro (MQ-2)** | GPIO 34 | ADC1 (Simulación Calidad del Aire 0-100%). |
| **BMP180** | I2C (SDA 21 / SCL 22) | Sensor de Presión Barométrica (Dirección `0x77`). |
| **OLED SSD1306** | I2C (SDA 21 / SCL 22) | Pantalla visualizadora (Dirección `0x3C`). |
| **LED Verde** | GPIO 26 | Estado Normal del sistema. |
| **LED Rojo** | GPIO 27 | Estado de Alerta activo. |
| **Buzzer** | GPIO 25 | Alarma sonora local. |

### Tópicos MQTT (`pro2/estacion01/`)
- **`telemetria`**: Lecturas consolidadas de sensores (JSON, QoS 0).
- **`estado`**: Estado de conexión `online`/`offline` mediante *Last Will and Testament* (QoS 1, Retain).
- **`alertas`**: Eventos generados al superar
