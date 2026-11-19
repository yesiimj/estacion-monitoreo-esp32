import tkinter as tk
from tkinter import ttk
from datetime import datetime
from simulador import SimuladorEstacion
from componentes import PanelSensores, PanelControl, PanelHistorial


class InterfazEstacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Estación de Monitoreo Ambiental - estacion01 (Simulación)")
        self.geometry("720x610")
        self.minsize(680, 580)

        self.simulador = SimuladorEstacion()
        self.pausado = False
        self.alerta_previa = False
        self.id_after = None

        self._configurar_estilos()
        self._construir_interfaz()
        self._registrar_evento("SISTEMA", "Interfaz iniciada en modo simulación local", "OK")
        self._ciclo_actualizacion()

    def _configurar_estilos(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

    def _construir_interfaz(self):
        frame_header = tk.Frame(self, bg="#1b263b", padx=15, pady=10)
        frame_header.pack(fill="x")

        tk.Label(
            frame_header,
            text="ESTACIÓN DE MONITOREO AMBIENTAL (ESP32)",
            bg="#1b263b",
            fg="white",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        self.lbl_info_sys = tk.Label(
            frame_header,
            text="ID: estacion01 | Modo: Simulado | Uptime: 0s",
            bg="#1b263b",
            fg="#a9d6e5",
            font=("Segoe UI", 9),
        )
        self.lbl_info_sys.pack(side="right")

        self.banner_alerta = tk.Label(
            self,
            text="ESTADO DEL SISTEMA: OPERACIÓN NORMAL",
            bg="#2e7d32",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            pady=6,
        )
        self.banner_alerta.pack(fill="x")

        contenedor = ttk.Frame(self, padding=12)
        contenedor.pack(fill="both", expand=True)

        self.panel_sensores = PanelSensores(contenedor)
        self.panel_sensores.pack(fill="x", pady=(0, 10))

        callbacks = {
            "actualizar_umbrales": self._actualizar_umbrales,
            "cambiar_intervalo": self._cambiar_intervalo,
            "cambiar_pantalla": self._cambiar_pantalla,
            "alternar_silencio": self._alternar_silencio,
            "alternar_pausa": self._alternar_pausa,
            "simular_pico": self._simular_pico,
        }
        self.panel_control = PanelControl(contenedor, callbacks)
        self.panel_control.pack(fill="x", pady=(0, 10))

        self.panel_historial = PanelHistorial(contenedor)
        self.panel_historial.pack(fill="both", expand=True)

        self.var_estado_barra = tk.StringVar(value="Listo | Intervalo: 2000 ms | OLED: auto")
        barra_estado = ttk.Label(self, textvariable=self.var_estado_barra, relief="sunken", anchor="w", padding=(10, 3))
        barra_estado.pack(fill="x", side="bottom")

    def _ciclo_actualizacion(self):
        if not self.pausado:
            datos = self.simulador.generar_lectura()
            self.panel_sensores.actualizar_vista(datos, self.simulador.umbrales)

            self.lbl_info_sys.config(
                text=f"ID: estacion01 | Modo: Simulado | Uptime: {datos['uptime_s']}s"
            )

            if datos["alerta"]:
                self.banner_alerta.config(
                    text=f"¡ALERTA ACTIVA! {datos['var_alerta']} = {datos['val_alerta']} (Umbral: {datos['umb_alerta']})",
                    bg="#c62828",
                )
                if not self.alerta_previa:
                    self._registrar_evento(
                        "ALARMA",
                        f"{datos['var_alerta']} superó umbral ({datos['val_alerta']} > {datos['umb_alerta']})",
                        "ALERTA",
                    )
            else:
                self.banner_alerta.config(text="ESTADO DEL SISTEMA: OPERACIÓN NORMAL", bg="#2e7d32")
                if self.alerta_previa:
                    self._registrar_evento("RECUPERACIÓN", "Variables dentro de rango seguro (histéresis OK)", "NORMAL")

            self.alerta_previa = datos["alerta"]

        self.id_after = self.after(self.simulador.intervalo_ms, self._ciclo_actualizacion)

    def _actualizar_umbrales(self, u_temp, u_hum, u_aire):
        self.simulador.umbrales = {"temp": u_temp, "hum": u_hum, "aire": u_aire}
        self._registrar_evento("CONFIG", f"Umbrales: T={u_temp}°C, H={u_hum}%, Aire={u_aire}%", "APLICADO")
        self._actualizar_barra_estado()

    def _cambiar_intervalo(self, ms):
        self.simulador.intervalo_ms = ms
        self._registrar_evento("CONFIG", f"Intervalo de muestreo ajustado a {ms} ms", "APLICADO")
        self._actualizar_barra_estado()

    def _cambiar_pantalla(self, modo):
        self.simulador.modo_pantalla = modo
        self._registrar_evento("OLED", f"Modo de pantalla remota cambiado a: {modo}", "ENVIADO")
        self._actualizar_barra_estado()

    def _alternar_silencio(self, silenciado):
        self.simulador.silenciado = silenciado
        estado = "SILENCIADO" if silenciado else "HABILITADO"
        self._registrar_evento("ACTUADOR", f"Buzzer {estado} por el usuario", estado)

    def _alternar_pausa(self, pausado):
        self.pausado = pausado
        estado = "PAUSADO" if pausado else "ACTIVO"
        self._registrar_evento("SISTEMA", f"Monitoreo {estado}", estado)

    def _simular_pico(self):
        self.simulador.forzar_pico = True
        self._registrar_evento("PRUEBA", "Simulación manual de sobrepaso de umbral solicitada", "TEST")

    def _actualizar_barra_estado(self):
        self.var_estado_barra.set(
            f"Listo | Intervalo: {self.simulador.intervalo_ms} ms | OLED: {self.simulador.modo_pantalla} | "
            f"Umbrales: T={self.simulador.umbrales['temp']}°C, H={self.simulador.umbrales['hum']}%, A={self.simulador.umbrales['aire']}%"
        )

    def _registrar_evento(self, tipo, detalle, estado):
        hora = datetime.now().strftime("%H:%M:%S")
        self.panel_historial.registrar(hora, tipo, detalle, estado)
