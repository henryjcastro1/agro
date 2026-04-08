import customtkinter as ctk
import json
import os
from tkinter import messagebox, ttk
from datetime import datetime

# Configurar tema
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

class ConfiguracionRecomendaciones:
    def __init__(self):
        self.ventana = ctk.CTk()
        self.ventana.title("Configurador de Recomendaciones - Laboratorio")
        self.ventana.geometry("1200x700")
        
        # Cargar configuración
        self.config_file = "config_recomendaciones.json"
        self.config = self.cargar_configuracion()
        
        # Variable para parámetro seleccionado
        self.parametro_actual = None
        self.indice_actual = None
        
        # Configurar UI
        self.setup_ui()
        
        # Cargar primer parámetro
        if self.config and list(self.config.keys()):
            self.parametro_combo.set(list(self.config.keys())[0])
            self.cargar_parametro(list(self.config.keys())[0])
    
    def cargar_configuracion(self):
        """Carga la configuración desde JSON"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar configuración: {e}")
                return self.crear_configuracion_default()
        else:
            return self.crear_configuracion_default()
    
    def crear_configuracion_default(self):
        """Crea configuración por defecto"""
        config_default = {
            "grasa": {
                "rangos": [
                    {"limite": 3.0, "mensaje": "Grasa < 3,0 % (NTC 399).\nPosibles causas: poca fibra efectiva, rumen acidótico, exceso de grano.\nRecomendaciones: aumentar fibra larga, reducir grano fino, añadir heno."},
                    {"limite": 3.4, "mensaje": "Grasa 3,0–3,4 % (Codex).\nPosibles causas: dietas bajas en fibra o cambios bruscos en la mezcla.\nRecomendaciones: mejorar FDN efectiva, estabilizar dieta."},
                    {"limite": 4.2, "mensaje": "Grasa 3,4–4,2 % (ICAR).\nBalance adecuado de fibra y energía.\nRecomendación: mantener manejo actual."},
                    {"limite": None, "mensaje": "Grasa > 4,2 % (ICAR).\nPosibles causas: dieta muy fibrosa, déficit energético.\nRecomendaciones: aumentar energía fermentable (maíz)."}
                ]
            },
            "proteina": {
                "rangos": [
                    {"limite": 3.0, "mensaje": "Proteína < 3,0 % (NTC 399).\nPosibles causas: dieta baja en energía, forraje pobre, rumen lento.\nRecomendaciones: incrementar energía, mejorar calidad del forraje."},
                    {"limite": 3.6, "mensaje": "Proteína 3,0–3,6 % (ICAR).\nBalance nutricional adecuado.\nRecomendación: mantener dieta y manejo."},
                    {"limite": None, "mensaje": "Proteína > 3,6 % (ICAR).\nPosibles causas: exceso de proteína.\nRecomendaciones: reducir PC en concentrado, revisar fertilización nitrogenada."}
                ]
            },
            "solidos_totales": {
                "rangos": [
                    {"limite": 11.3, "mensaje": "ST < 11,3 % (NTC 399).\nPosibles causas: leche diluida, mala nutrición, posible adulteración.\nRecomendaciones: revisar FPD, mejorar consumo de materia seca."},
                    {"limite": 11.8, "mensaje": "ST 11,3–11,8 % (MinSalud).\nPosibles causas: forraje de baja calidad, vacas recién paridas.\nRecomendaciones: incrementar energía."},
                    {"limite": 13.2, "mensaje": "ST 11,8–13,2 % (ICAR).\nComposición ideal.\nRecomendación: mantener manejo nutricional."},
                    {"limite": None, "mensaje": "ST > 13,2 % (ICAR).\nPosibles causas: deshidratación o leche muy concentrada.\nRecomendaciones: revisar acceso al agua, evaluar estrés térmico."}
                ]
            },
            "ufc": {
                "rangos": [
                    {"limite": 25000, "mensaje": "UFC < 25.000 (ICAR).\nExcelente higiene y buen enfriamiento.\nRecomendación: mantener rutina CIP y temperatura del tanque."},
                    {"limite": 100000, "mensaje": "UFC 25–100k (Res. 017/2012).\nLavado inestable.\nRecomendaciones: revisar CIP, detergente y temperatura del agua."},
                    {"limite": 300000, "mensaje": "UFC 100–300k (ICAR).\nBiofilm o deficiencia en lavado.\nRecomendaciones: CIP alcalino + ácido, cambiar gomas, reforzar higiene."},
                    {"limite": None, "mensaje": "UFC > 300k (MinAgricultura).\nContaminación severa, riesgo sanitario.\nRecomendaciones: auditoría completa, limpieza profunda, revisar cadena de frío."}
                ]
            },
            "celulas_somaticas": {
                "rangos": [
                    {"limite": 200000, "mensaje": "Cs < 200.000 (DHIA).\nHigiene adecuada.\nRecomendaciones: mantener pre y post sellado, revisar pezoneras."},
                    {"limite": 400000, "mensaje": "Cs 200–400.000 (DHIA).\nInicio de inflamación.\nRecomendaciones: CMT a vacas frescas, verificar pulsación y vacío."},
                    {"limite": 700000, "mensaje": "Cs 400–700.000 (NTC 399).\nMastitis subclínica.\nRecomendaciones: segregar vacas problema, realizar tratamiento."},
                    {"limite": None, "mensaje": "Cs > 700.000 (NTC 399).\nLeche fuera de norma.\nRecomendaciones: auditoría del equipo, reemplazo de pezoneras, higiene estricta."}
                ]
            },
            "lactosa": {
                "rangos": [
                    {"limite": 4.5, "mensaje": "Lactosa < 4,5 % (DHIA).\nPosibles causas: mastitis subclínica, estrés calórico.\nRecomendaciones: realizar CMT, mejorar ventilación y acceso al agua."},
                    {"limite": 4.9, "mensaje": "Lactosa 4,5–4,9 % (ICAR).\nSalud de ubre adecuada.\nRecomendación: mantener rutina y manejo."},
                    {"limite": None, "mensaje": "Lactosa > 4,9 % (DHIA).\nAlta producción o vacas frescas.\nRecomendación: monitoreo."}
                ]
            },
            "urea": {
                "rangos": [
                    {"limite": 10, "mensaje": "Urea < 10 mg/dL (NRC/UCC).\nPasto maduro o baja proteína degradable.\nRecomendaciones: aumentar proteína degradable, mejorar rotación del forraje."},
                    {"limite": 18, "mensaje": "Urea 10–18 mg/dL (NRC/DHIA).\nDieta balanceada.\nRecomendación: mantener estabilidad en la dieta."},
                    {"limite": 22, "mensaje": "Urea 18–22 mg/dL (DHIA).\nExceso de proteína soluble.\nRecomendaciones: reducir PC, aumentar energía fermentable."},
                    {"limite": None, "mensaje": "Urea > 22 mg/dL (DHIA).\nSobreoferta proteica severa, riesgo reproductivo.\nRecomendaciones: reducir proteína inmediatamente, revisar BCS y servicios."}
                ]
            },
            "fpd": {
                "rangos": [
                    {"limite": -0.530, "mensaje": "FPD ≤ –0,530 (NTC 399).\nLeche normal.\nRecomendación: mantener cadena de frío."},
                    {"limite": -0.510, "mensaje": "FPD –0,530 a –0,510 (NTC 399).\nLigera variación normal.\nRecomendación: verificar temperatura del tanque."},
                    {"limite": None, "mensaje": "FPD > –0,510 (NTC 399).\nPosible adición de agua o enfriamiento lento.\nRecomendaciones: revisar rutina de enfriamiento, auditar mezcla agua–leche."}
                ]
            }
        }
        
        # Guardar configuración por defecto
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_default, f, indent=2, ensure_ascii=False)
        
        return config_default
    
    def guardar_configuracion(self):
        """Guarda la configuración en JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Éxito", "✅ Configuración guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al guardar: {e}")
    
    def setup_ui(self):
        """Configura la interfaz"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.ventana)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(
            main_frame, 
            text="📊 EDITOR DE RECOMENDACIONES - PARÁMETROS DE CALIDAD DE LECHE",
            font=("Arial", 18, "bold")
        )
        titulo.pack(pady=10)
        
        # Frame para selección de parámetro
        seleccion_frame = ctk.CTkFrame(main_frame)
        seleccion_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(seleccion_frame, text="📌 Seleccionar Parámetro:", font=("Arial", 14)).pack(side="left", padx=10)
        
        self.parametro_combo = ctk.CTkComboBox(
            seleccion_frame,
            values=list(self.config.keys()),
            width=200,
            command=self.cargar_parametro
        )
        self.parametro_combo.pack(side="left", padx=10)
        
        # Frame principal de edición
        editor_frame = ctk.CTkFrame(main_frame)
        editor_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Columna izquierda - Lista de rangos
        left_frame = ctk.CTkFrame(editor_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(left_frame, text="📋 RANGOS Y LÍMITES", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Treeview
        self.tree_frame = ctk.CTkFrame(left_frame)
        self.tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=("Rango", "Mensaje"), show="tree headings", height=15)
        self.tree.heading("Rango", text="Rango de valores")
        self.tree.heading("Mensaje", text="Mensaje de recomendación")
        self.tree.column("Rango", width=150)
        self.tree.column("Mensaje", width=400)
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select_rango)
        
        # Columna derecha - Editor
        right_frame = ctk.CTkFrame(editor_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(right_frame, text="✏️ EDITAR MENSAJE", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.info_label = ctk.CTkLabel(right_frame, text="Seleccione un rango de la lista", font=("Arial", 12))
        self.info_label.pack(pady=5)
        
        self.texto_mensaje = ctk.CTkTextbox(right_frame, height=300, width=500, wrap="word")
        self.texto_mensaje.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botones
        button_frame = ctk.CTkFrame(right_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="💾 Guardar Cambios", command=self.guardar_mensaje, fg_color="green").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="🔄 Recargar", command=self.recargar_configuracion, fg_color="orange").pack(side="left", padx=5)
        
        # Frame para agregar rango
        add_frame = ctk.CTkFrame(main_frame)
        add_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(add_frame, text="➕ AGREGAR NUEVO RANGO:", font=("Arial", 12)).pack(side="left", padx=5)
        
        ctk.CTkLabel(add_frame, text="Límite:").pack(side="left", padx=5)
        self.nuevo_limite = ctk.CTkEntry(add_frame, width=100, placeholder_text="ej: 5.0")
        self.nuevo_limite.pack(side="left", padx=5)
        
        ctk.CTkLabel(add_frame, text="Mensaje:").pack(side="left", padx=5)
        self.nuevo_mensaje = ctk.CTkEntry(add_frame, width=300, placeholder_text="Texto del mensaje...")
        self.nuevo_mensaje.pack(side="left", padx=5)
        
        ctk.CTkButton(add_frame, text="➕ Agregar", command=self.agregar_rango, fg_color="blue").pack(side="left", padx=5)
        ctk.CTkButton(add_frame, text="🗑 Eliminar", command=self.eliminar_rango, fg_color="red").pack(side="left", padx=5)
        
        # Botones principales
        main_buttons = ctk.CTkFrame(main_frame)
        main_buttons.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(main_buttons, text="💾 GUARDAR TODO", command=self.guardar_configuracion, height=40, fg_color="green", font=("Arial", 14, "bold")).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(main_buttons, text="📊 PROBAR MUESTRA", command=self.mostrar_ejemplo, height=40, fg_color="blue").pack(side="left", padx=5, expand=True, fill="x")
    
    def cargar_parametro(self, parametro):
        """Carga el parámetro seleccionado"""
        self.parametro_actual = parametro
        self.actualizar_tree()
    
    def actualizar_tree(self):
        """Actualiza el treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.parametro_actual:
            return
        
        parametro_data = self.config[self.parametro_actual]
        
        for i, rango in enumerate(parametro_data["rangos"]):
            limite = rango["limite"]
            
            if limite is None:
                if i == 0:
                    texto_rango = "Todos los valores"
                else:
                    anterior = parametro_data["rangos"][i-1]["limite"]
                    texto_rango = f"> {anterior}"
            elif i == 0:
                texto_rango = f"< {limite}"
            else:
                anterior = parametro_data["rangos"][i-1]["limite"]
                texto_rango = f"{anterior} – {limite}"
            
            preview = rango["mensaje"][:80] + "..." if len(rango["mensaje"]) > 80 else rango["mensaje"]
            preview = preview.replace("\n", " ")
            
            self.tree.insert("", "end", iid=str(i), values=(texto_rango, preview))
    
    def on_select_rango(self, event):
        """Selecciona un rango"""
        selection = self.tree.selection()
        if selection:
            idx = int(selection[0])
            rango = self.config[self.parametro_actual]["rangos"][idx]
            
            limite = rango["limite"]
            if limite is None:
                texto_limite = "Sin límite superior"
            else:
                texto_limite = f"Límite: {limite}"
            
            self.info_label.configure(text=f"📌 Editando: {texto_limite}")
            
            self.texto_mensaje.delete("1.0", "end")
            self.texto_mensaje.insert("1.0", rango["mensaje"])
            
            self.indice_actual = idx
    
    def guardar_mensaje(self):
        """Guarda el mensaje editado"""
        if self.indice_actual is None:
            messagebox.showwarning("Advertencia", "Seleccione un rango primero")
            return
        
        nuevo_mensaje = self.texto_mensaje.get("1.0", "end-1c")
        if not nuevo_mensaje.strip():
            messagebox.showwarning("Advertencia", "El mensaje no puede estar vacío")
            return
        
        self.config[self.parametro_actual]["rangos"][self.indice_actual]["mensaje"] = nuevo_mensaje
        self.actualizar_tree()
        messagebox.showinfo("Éxito", "Mensaje actualizado")
    
    def agregar_rango(self):
        """Agrega un nuevo rango"""
        limite = self.nuevo_limite.get().strip()
        mensaje = self.nuevo_mensaje.get().strip()
        
        if not mensaje:
            messagebox.showwarning("Advertencia", "Debe ingresar un mensaje")
            return
        
        if limite == '' or limite.lower() == 'null':
            limite = None
        else:
            try:
                limite = float(limite)
            except:
                messagebox.showerror("Error", "El límite debe ser un número")
                return
        
        nuevo_rango = {"limite": limite, "mensaje": mensaje}
        self.config[self.parametro_actual]["rangos"].append(nuevo_rango)
        
        # Ordenar
        rangos = self.config[self.parametro_actual]["rangos"]
        rangos.sort(key=lambda x: x["limite"] if x["limite"] is not None else float('inf'))
        
        self.actualizar_tree()
        self.nuevo_limite.delete(0, 'end')
        self.nuevo_mensaje.delete(0, 'end')
        messagebox.showinfo("Éxito", "Rango agregado")
    
    def eliminar_rango(self):
        """Elimina el rango seleccionado"""
        if self.indice_actual is None:
            messagebox.showwarning("Advertencia", "Seleccione un rango primero")
            return
        
        if len(self.config[self.parametro_actual]["rangos"]) <= 1:
            messagebox.showerror("Error", "Debe haber al menos un rango")
            return
        
        confirmar = messagebox.askyesno("Confirmar", "¿Eliminar este rango?")
        if confirmar:
            del self.config[self.parametro_actual]["rangos"][self.indice_actual]
            self.actualizar_tree()
            self.texto_mensaje.delete("1.0", "end")
            self.indice_actual = None
            messagebox.showinfo("Éxito", "Rango eliminado")
    
    def recargar_configuracion(self):
        """Recarga la configuración"""
        self.config = self.cargar_configuracion()
        if self.parametro_actual:
            self.cargar_parametro(self.parametro_actual)
        messagebox.showinfo("Info", "Configuración recargada")
    
    def mostrar_ejemplo(self):
        """Muestra un ejemplo"""
        from recommender import recomendar_con_valores_por_defecto
        
        muestra = {
            "grasa": "2.8",
            "proteina": "3.2",
            "solidos": "12.5",
            "mesofilas": "150000",
            "celulas": "350000",
            "lactosa": "4.7",
            "n_ureico": "15",
            "p_crioscopico": "-0.520"
        }
        
        recomendaciones = recomendar_con_valores_por_defecto(muestra)
        
        ventana = ctk.CTkToplevel(self.ventana)
        ventana.title("Ejemplo")
        ventana.geometry("600x500")
        
        texto = ctk.CTkTextbox(ventana, wrap="word")
        texto.pack(fill="both", expand=True, padx=10, pady=10)
        texto.insert("1.0", recomendaciones)
        texto.configure(state="disabled")
    
    def run(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    app = ConfiguracionRecomendaciones()
    app.run()