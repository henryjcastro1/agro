import json
import os

CONFIG_FILE = "config_recomendaciones.json"

def crear_configuracion_default():
    """Crea la configuración por defecto y la guarda en archivo"""
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
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_default, f, indent=2, ensure_ascii=False)
    
    return config_default

def cargar_configuracion():
    """Carga la configuración de recomendaciones. Si no existe, la crea."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠ Error cargando configuración: {e}")
            print("📝 Creando configuración por defecto...")
            return crear_configuracion_default()
    else:
        print("📝 Archivo de configuración no encontrado. Creando configuración por defecto...")
        return crear_configuracion_default()

def recomendar(m):
    """Genera recomendaciones basadas en configuración"""
    config = cargar_configuracion()
    recs = []
    
    # Parámetros
    grasa = float(m["grasa"])
    proteina = float(m["proteina"])
    st = float(m["solidos"])
    ufc = int(m["mesofilas"])
    cs = int(m["celulas"])
    lactosa = float(m["lactosa"])
    urea = float(m["n_ureico"])
    fpd = float(m["p_crioscopico"])
    
    # Función auxiliar para evaluar rangos
    def evaluar_parametro(valor, parametro_config):
        rangos = parametro_config["rangos"]
        
        # Ordenar rangos por límite (None al final)
        rangos_ordenados = sorted(rangos, key=lambda x: x["limite"] if x["limite"] is not None else float('inf'))
        
        for i, rango in enumerate(rangos_ordenados):
            limite = rango["limite"]
            
            # Si es el último rango (sin límite superior)
            if limite is None:
                # Verificar si es mayor que el límite anterior
                if i > 0:
                    limite_anterior = rangos_ordenados[i-1]["limite"]
                    if valor >= limite_anterior:
                        return rango["mensaje"]
                else:
                    # Si es el único rango, siempre aplica
                    return rango["mensaje"]
            
            # Primer rango (valores menores al primer límite)
            elif i == 0:
                if valor < limite:
                    return rango["mensaje"]
            
            # Rangos medios (entre límite anterior y actual)
            else:
                limite_anterior = rangos_ordenados[i-1]["limite"]
                if limite_anterior <= valor < limite:
                    return rango["mensaje"]
        
        # Si no encontró ningún rango, usar el último
        return rangos_ordenados[-1]["mensaje"] if rangos_ordenados else "Sin recomendación disponible"
    
    # Evaluar cada parámetro
    try:
        recs.append(evaluar_parametro(grasa, config["grasa"]))
        recs.append(evaluar_parametro(proteina, config["proteina"]))
        recs.append(evaluar_parametro(st, config["solidos_totales"]))
        recs.append(evaluar_parametro(ufc, config["ufc"]))
        recs.append(evaluar_parametro(cs, config["celulas_somaticas"]))
        recs.append(evaluar_parametro(lactosa, config["lactosa"]))
        recs.append(evaluar_parametro(urea, config["urea"]))
        recs.append(evaluar_parametro(fpd, config["fpd"]))
    except KeyError as e:
        print(f"⚠ Error: Falta la configuración para {e}. Usando valores por defecto...")
        return recomendar_con_valores_por_defecto(m)
    
    # Filtrar mensajes duplicados
    recs_unicas = []
    for rec in recs:
        if rec not in recs_unicas:
            recs_unicas.append(rec)
    
    return "\n\n".join(recs_unicas)


# Función de respaldo para pruebas sin archivo JSON
def recomendar_con_valores_por_defecto(m):
    """Versión de respaldo con valores por defecto (sin necesidad de JSON)"""
    recs = []
    
    grasa = float(m["grasa"])
    proteina = float(m["proteina"])
    st = float(m["solidos"])
    ufc = int(m["mesofilas"])
    cs = int(m["celulas"])
    lactosa = float(m["lactosa"])
    urea = float(m["n_ureico"])
    fpd = float(m["p_crioscopico"])
    
    # Grasa
    if grasa < 3.0:
        recs.append("⚠️ Grasa baja (< 3.0%): Revisar alimentación, aumentar fibra")
    elif grasa > 4.2:
        recs.append("⚠️ Grasa alta (> 4.2%): Posible déficit energético")
    else:
        recs.append("✅ Grasa en rango normal (3.0-4.2%)")
    
    # Proteína
    if proteina < 3.0:
        recs.append("⚠️ Proteína baja (< 3.0%): Mejorar calidad del forraje")
    elif proteina > 3.6:
        recs.append("⚠️ Proteína alta (> 3.6%): Reducir proteína en dieta")
    else:
        recs.append("✅ Proteína en rango normal (3.0-3.6%)")
    
    # Sólidos totales
    if st < 11.3:
        recs.append("⚠️ Sólidos totales bajos (< 11.3%): Posible adulteración")
    elif st > 13.2:
        recs.append("⚠️ Sólidos totales altos (> 13.2%): Posible deshidratación")
    else:
        recs.append("✅ Sólidos totales en rango normal (11.3-13.2%)")
    
    # UFC
    if ufc < 25000:
        recs.append("✅ Excelente higiene (UFC < 25,000)")
    elif ufc > 300000:
        recs.append("⚠️ Contaminación severa (UFC > 300,000): Revisar limpieza")
    else:
        recs.append("⚠️ UFC en rango aceptable, monitorear")
    
    # Células somáticas
    if cs < 200000:
        recs.append("✅ Buena salud de ubre (CS < 200,000)")
    elif cs > 700000:
        recs.append("⚠️ Mastitis severa (CS > 700,000): Tratamiento urgente")
    else:
        recs.append("⚠️ CS en rango de monitoreo")
    
    # Lactosa
    if lactosa < 4.5:
        recs.append("⚠️ Lactosa baja (< 4.5%): Posible mastitis")
    else:
        recs.append("✅ Lactosa en rango normal")
    
    # Urea
    if urea < 10:
        recs.append("⚠️ Urea baja (< 10 mg/dL): Déficit de proteína")
    elif urea > 22:
        recs.append("⚠️ Urea alta (> 22 mg/dL): Exceso de proteína")
    else:
        recs.append("✅ Urea en rango balanceado (10-22 mg/dL)")
    
    # FPD
    if fpd > -0.510:
        recs.append("⚠️ Posible adulteración con agua (FPD elevado)")
    else:
        recs.append("✅ FPD normal")
    
    return "\n\n".join(recs)


# Función para probar la configuración
def probar_recomendaciones():
    """Función de prueba con datos de ejemplo"""
    muestra_ejemplo = {
        "grasa": "3.2",
        "proteina": "3.1",
        "solidos": "12.0",
        "mesofilas": "50000",
        "celulas": "250000",
        "lactosa": "4.7",
        "n_ureico": "15",
        "p_crioscopico": "-0.520"
    }
    
    print("=== Probando recomendaciones ===")
    resultado = recomendar(muestra_ejemplo)
    print(resultado)


if __name__ == "__main__":
    probar_recomendaciones()