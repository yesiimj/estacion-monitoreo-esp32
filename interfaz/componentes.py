import tkinter as tk
from tkinter import ttk, messagebox


class PanelSensores(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text=" Monitoreo de Variables y Actuadores ", padding=12)
        self._construir_widgets()

    def _construir_widgets(self):
        self.var_temp = tk.StringVar(value="-- °C")
        self.var_hum = tk.StringVar(value="-- %")
        self.var_pres = tk.StringVar(value="-- hPa")
        self.var_aire = tk.StringVar(value="-- % (Buena)")

        ttk.Label(self, text="Temperatura (DHT22):", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        self.lbl_temp = ttk.Label(self, textvariable=self.var_temp, font=("Segoe UI", 13, "bold"), foreground="#1f6aa5")
        self.lbl_temp.grid(row=0, column=1, sticky="w", padx=10)

        ttk.Label(self, text="Humedad Relativa:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        self.lbl_hum = ttk.Label(self, textvariable=self.var_hum, font=("Segoe UI", 13, "bold"), foreground="#1f6aa5")
        self.lbl_hum.grid(row=1, column=1, sticky="w", padx=10)

        self.barra_hum = ttk.Progressbar(self, orient="horizontal", length=180, mode="determinate", maximum=100)
        self.barra_hum.grid(row=1, column=2, padx=10)

        ttk.Label(self, text="Presión (BMP180):", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        ttk.Label(self, textvariable=self.var_pres, font=("Segoe UI", 13, "bold"), foreground="#2e7d32").grid(row=2, column=1, sticky="w", padx=10)

        ttk.Label(self, text="Calidad del Aire (MQ-2):", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=4)
        self.lbl_aire = ttk.Label(self, textvariable=self.var_aire, font=("Segoe UI", 13, "bold"), foreground="#2e7d32")
        self.lbl_aire.grid(row=3, column=1, sticky="w", padx=10)

        self.barra_aire = ttk.Progressbar(self, orient="horizontal", length=180, mode="determinate", maximum=100)
        self.barra_aire.grid(row=3, column=2, padx=10)

        ttk.Separator(self, orient="horizontal").grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)

        frame_leds = ttk.Frame(self)
        frame_leds.grid(row=5, column=0, columnspan=3, sticky="w")

        self.lbl_led_verde = tk.Label(frame_leds, text=" ● LED VERDE (OK) ", bg="#2e7d32", fg="white", font=("Segoe UI", 9, "bold"), padx=8, pady=4)
        self.lbl_led_verde.pack(side="left", padx=(0, 10))

        self.lbl_led_rojo = tk.Label(frame_leds, text=" ● LED ROJO (ALERTA) ", bg="#bdbdbd", fg="#424242", font=("Segoe UI", 9, "bold"), padx=8, pady=4)
        self.lbl_led_rojo.pack(side="left", padx=(0, 10))

        self.lbl_buzzer = tk.Label(frame_leds, text=" BUZZER: APAGADO ", bg="#eeeeee", fg="#333333", font=("Segoe UI", 9, "bold"), padx=8, pady=4)
        self.lbl_buzzer.pack(side="left")

    def actualizar_vista(self, datos, umbrales):
        self.var_temp.set(f"{datos['temp']:.1f} °C")
        self.var_hum.set(f"{datos['hum']:.1f} %")
        self.var_pres.set(f"{datos['pres']:.1f} hPa")
        self.var_aire.set(f"{datos['aire']} % ({datos['categoria']})")

        self.barra_hum["value"] = datos["hum"]
        self.barra_aire["value"] = datos["aire"]

        self.lbl_temp.config(foreground="#c62828" if datos["temp"] > umbrales["temp"] else "#1f6aa5")
        self.lbl_hum.config(foreground="#c62828" if datos["hum"] > umbrales["hum"] else "#1f6aa5")
        self.lbl_aire.config(foreground="#c62828" if datos["aire"] > umbrales["aire"] else "#2e7d32")

        if datos["led_verde"]:
            self.lbl_led_verde.config(bg="#2e7d32", fg="white")
            self.lbl_led_rojo.config(bg="#bdbdbd", fg="#424242")
        else:
            self.lbl_led_verde.config(bg="#bdbdbd", fg="#424242")
            self.lbl_led_rojo.config(bg="#c62828", fg="white")

        if datos["buzzer_activo"]:
            self.lbl_buzzer.config(text=" BUZZER: SONANDO ", bg="#f57c00", fg="white")
        else:
            self.lbl_buzzer.config(text=" BUZZER: APAGADO ", bg="#eeeeee", fg="#333333")


class PanelControl(ttk.LabelFrame):
    def __init__(self, parent, callbacks):
        super().__init__(parent, text=" Configuración y Control Remoto ", padding=12)
        self.callbacks = callbacks
        self.silenciado = False
        self.pausado = False
        self._construir_widgets()

    def _construir_widgets(self):
        ttk.Label(self, text="Umbral Temp (°C):").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_temp = ttk.Entry(self, width=10)
        self.entry_temp.insert(0, "35.0")
        self.entry_temp.grid(row=0, column=1, padx=6, pady=3)

        ttk.Label(self, text="Umbral Hum (%):").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_hum = ttk.Entry(self, width=10)
        self.entry_hum.insert(0, "80.0")
        self.entry_hum.grid(row=1, column=1, padx=6, pady=3)

        ttk.Label(self, text="Umbral Aire (%):").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_aire = ttk.Entry(self, width=10)
        self.entry_aire.insert(0, "60")
        self.entry_aire.grid(row=2, column=1, padx=6, pady=3)

        for campo in (self.entry_temp, self.entry_hum, self.entry_aire):
            campo.bind("<Return>", lambda event: self._validar_y_aplicar())

        self.btn_aplicar = ttk.Button(self, text="Aplicar Umbrales", command=self._validar_y_aplicar)
        self.btn_aplicar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 10))

        ttk.Label(self, text="Intervalo Muestreo:").grid(row=0, column=2, sticky="w", padx=(15, 4))
        self.combo_intervalo = ttk.Combobox(
            self, values=["2000 ms", "3000 ms", "5000 ms", "10000 ms"], state="readonly", width=13
        )
        self.combo_intervalo.current(0)
        self.combo_intervalo.grid(row=0, column=3, padx=4)
        self.combo_intervalo.bind("<<ComboboxSelected>>", self._evento_intervalo)

        ttk.Label(self, text="Página OLED:").grid(row=1, column=2, sticky="w", padx=(15, 4))
        self.combo_pantalla = ttk.Combobox(
            self,
            values=["auto", "0 - Temp/Hum", "1 - Presión", "2 - Calidad Aire", "3 - Estado Red"],
            state="readonly",
            width=13,
        )
        self.combo_pantalla.current(0)
        self.combo_pantalla.grid(row=1, column=3, padx=4)
        self.combo_pantalla.bind("<<ComboboxSelected>>", self._evento_pantalla)

        self.btn_silencio = ttk.Button(self, text="Silenciar Buzzer", command=self._alternar_silencio)
        self.btn_silencio.grid(row=2, column=2, columnspan=2, sticky="ew", padx=(15, 4), pady=3)

        frame_acciones = ttk.Frame(self)
        frame_acciones.grid(row=3, column=2, columnspan=2, sticky="ew", padx=(15, 4), pady=(6, 10))

        self.btn_pausa = ttk.Button(frame_acciones, text="Pausar", command=self._alternar_pausa)
        self.btn_pausa.pack(side="left", expand=True, fill="x", padx=(0, 3))

        self.btn_simular_pico = ttk.Button(frame_acciones, text="Simular Alerta", command=self.callbacks["simular_pico"])
        self.btn_simular_pico.pack(side="left", expand=True, fill="x", padx=(3, 0))

    def _validar_y_aplicar(self):
        try:
            u_temp = float(self.entry_temp.get())
            u_hum = float(self.entry_hum.get())
            u_aire = int(float(self.entry_aire.get()))

            if not (0 <= u_temp <= 80):
                raise ValueError("La temperatura umbral debe estar entre 0 °C y 80 °C.")
            if not (10 <= u_hum <= 100):
                raise ValueError("La humedad umbral debe estar entre 10 % y 100 %.")
            if not (5 <= u_aire <= 100):
                raise ValueError("El umbral de aire debe estar entre 5 % y 100 %.")

            self.callbacks["actualizar_umbrales"](u_temp, u_hum, u_aire)
        except ValueError as err:
            messagebox.showerror("Error de Validación", f"Dato inválido:\n{err}")

    def _evento_intervalo(self, event):
        seleccion = self.combo_intervalo.get()
        ms = int(seleccion.split()[0])
        self.callbacks["cambiar_intervalo"](ms)

    def _evento_pantalla(self, event):
        seleccion = self.combo_pantalla.get()
        modo = "auto" if seleccion == "auto" else seleccion[0]
        self.callbacks["cambiar_pantalla"](modo)

    def _alternar_silencio(self):
        self.silenciado = not self.silenciado
        self.btn_silencio.config(text="Activar Buzzer" if self.silenciado else "Silenciar Buzzer")
        self.callbacks["alternar_silencio"](self.silenciado)

    def _alternar_pausa(self):
        self.pausado = not self.pausado
        self.btn_pausa.config(text="Reanudar" if self.pausado else "Pausar")
        self.callbacks["alternar_pausa"](self.pausado)


class PanelHistorial(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text=" Historial de Eventos y Alarmas (Doble clic para detalle) ", padding=10)
        self._construir_widgets()

    def _construir_widgets(self):
        columnas = ("hora", "tipo", "detalle", "estado")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=7)

        self.tabla.heading("hora", text="Hora")
        self.tabla.heading("tipo", text="Categoría")
        self.tabla.heading("detalle", text="Descripción del Evento")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("hora", width=85, anchor="center")
        self.tabla.column("tipo", width=110, anchor="center")
        self.tabla.column("detalle", width=330, anchor="w")
        self.tabla.column("estado", width=95, anchor="center")

        scroll = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        self.tabla.bind("<Double-1>", self._mostrar_detalle)

        btn_limpiar = ttk.Button(self, text="Limpiar Historial", command=self.limpiar)
        btn_limpiar.grid(row=1, column=0, sticky="e", pady=(6, 0))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def registrar(self, hora, tipo, detalle, estado):
        self.tabla.insert("", 0, values=(hora, tipo, detalle, estado))

    def limpiar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

    def _mostrar_detalle(self, event):
        seleccion = self.tabla.selection()
        if seleccion:
            valores = self.tabla.item(seleccion[0], "values")
            messagebox.showinfo(
                "Detalle del Evento",
                f"Hora: {valores[0]}\nCategoría: {valores[1]}\nDetalle: {valores[2]}\nEstado: {valores[3]}",
            )
