from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import json
import schedule
import time
import shutil
from datetime import datetime

from db import SessionLocal, engine, Base
from models import Rad, Sample
from parser import parse_pdf
from recommender import recomendar

PDF_FOLDER = "pdfs"
PROCESSED_FILE = "processed.json"
CARPETA_OUTPUTS = "outputs_combinados"

# ================= INICIALIZAR BASE =================

def init_db():
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    os.makedirs(CARPETA_OUTPUTS, exist_ok=True)

# ================= UTILIDADES =================

def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return []
    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_processed(lst):
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(lst, f, indent=2, ensure_ascii=False)

# ================= GENERAR Y COMBINAR PDFs =================

def generar_y_combinar_pdfs(db, archivo_original, carpeta_salida="outputs_combinados"):
    """
    Genera PDF de recomendaciones y lo combina con el original
    """
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from PyPDF2 import PdfReader, PdfWriter
    
    # Colores
    COLOR_PRIMARIO = colors.HexColor("#006837")
    COLOR_SECUNDARIO = colors.HexColor("#003366")
    COLOR_GRIS = colors.HexColor("#F2F2F2")
    
    # Obtener el RAD más reciente (el que acabamos de procesar)
    rad = db.query(Rad).order_by(Rad.id.desc()).first()
    if not rad:
        print("   ⚠ No hay RAD en la base de datos")
        return None
    
    # Generar PDF de recomendaciones
    nombre_base = os.path.splitext(os.path.basename(archivo_original))[0]
    ruta_recomendaciones = os.path.join(carpeta_salida, f"{nombre_base}_recomendaciones_temp.pdf")
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TituloVerde", fontName="Helvetica-Bold", fontSize=12, textColor=COLOR_PRIMARIO, spaceAfter=10))
    styles.add(ParagraphStyle(name="Subtitulo", fontName="Helvetica-Bold", fontSize=10, textColor=COLOR_SECUNDARIO))
    
    doc = SimpleDocTemplate(ruta_recomendaciones, pagesize=landscape(letter), leftMargin=30, rightMargin=30, topMargin=100, bottomMargin=40)
    elements = []
    
    def header(canvas, doc):
        canvas.saveState()
        width, height = landscape(letter)
        canvas.setStrokeColor(COLOR_PRIMARIO)
        canvas.setLineWidth(2)
        canvas.line(30, height - 90, width - 30, height - 90)
        canvas.setFont("Helvetica-Bold", 13)
        canvas.setFillColor(COLOR_SECUNDARIO)
        canvas.drawRightString(width - 30, height - 50, "RECOMENDACIONES DE LABORATORIO")
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.black)
        canvas.drawRightString(width - 30, 20, f"Página {doc.page}")
        canvas.restoreState()
    
    # Agregar información del RAD
    elements.append(Paragraph(f"RAD: {rad.rad_code}", styles["TituloVerde"]))
    elements.append(Paragraph(f"Cliente: {rad.cliente}", styles["Normal"]))
    elements.append(Paragraph(f"Fecha: {rad.fecha}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    
    # Agregar muestras y recomendaciones
    for s in rad.samples:
        elements.append(Paragraph(f"Muestra: {s.code}", styles["Subtitulo"]))
        elements.append(Spacer(1, 6))
        
        data = [
            ["Grasa", "Proteína", "ST", "Urea", "CS", "UFC", "Lactosa", "FPD"],
            [s.grasa, s.proteina, s.solidos, s.n_ureico, s.celulas, s.mesofilas, s.lactosa, s.p_crioscopico],
        ]
        
        table = Table(data, colWidths=[75] * 8)
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARIO),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), COLOR_GRIS),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 10))
        
        texto = (s.recomendaciones or "Sin recomendaciones").replace("\n", "<br/>")
        elements.append(Paragraph("Recomendaciones técnicas:", styles["Subtitulo"]))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph(texto, styles["Normal"]))
        elements.append(Spacer(1, 20))
    
    doc.build(elements, onFirstPage=header, onLaterPages=header)
    
    # Combinar PDF original con recomendaciones
    ruta_combinado = os.path.join(carpeta_salida, f"{nombre_base}_COMPLETO.pdf")
    
    writer = PdfWriter()
    
    # Agregar PDF original
    with open(archivo_original, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            writer.add_page(page)
    
    # Agregar PDF de recomendaciones
    with open(ruta_recomendaciones, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            writer.add_page(page)
    
    # Guardar combinado
    with open(ruta_combinado, 'wb') as f:
        writer.write(f)
    
    # Eliminar temporal
    os.remove(ruta_recomendaciones)
    
    return ruta_combinado

# ================= PROCESO PRINCIPAL =================

def process_pdfs():
    print("\n" + "="*60)
    print("PROCESANDO PDFS")
    print("="*60)

    if not os.path.exists(PDF_FOLDER):
        print(f"⚠ La carpeta '{PDF_FOLDER}' no existe.")
        return

    processed = load_processed()
    nuevos = 0

    db = SessionLocal()

    for file in os.listdir(PDF_FOLDER):
        if not file.lower().endswith(".pdf"):
            continue

        fullpath = os.path.join(PDF_FOLDER, file)

        if fullpath in processed:
            print(f"⏭ Saltando (ya procesado): {file}")
            continue

        print(f"\n➜ Leyendo {file}")

        try:
            parsed = parse_pdf(fullpath)
            
            # Validar que se haya extraído información
            if not parsed["rad"]:
                print(f"   ⚠ No se pudo extraer RAD del PDF")
                continue

            # Guardar en BD
            rad = Rad(
                rad_code=parsed["rad"],
                cliente=parsed["cliente"],
                fecha=parsed["fecha"]
            )
            db.add(rad)
            db.commit()
            db.refresh(rad)

            for m in parsed["samples"]:
                recs = recomendar(m)
                sample = Sample(
                    rad_id=rad.id,
                    code=m["code"],
                    n_ureico=m["n_ureico"],
                    celulas=m["celulas"],
                    grasa=m["grasa"],
                    lactosa=m["lactosa"],
                    p_crioscopico=m["p_crioscopico"],
                    proteina=m["proteina"],
                    solidos=m["solidos"],
                    mesofilas=m["mesofilas"],
                    recomendaciones=recs
                )
                db.add(sample)

            db.commit()

            # Generar PDF combinado (original + recomendaciones)
            pdf_combinado = generar_y_combinar_pdfs(db, fullpath)
            
            if pdf_combinado:
                print(f"   ✓ PDF combinado generado: {os.path.basename(pdf_combinado)}")
            
            processed.append(fullpath)
            nuevos += 1
            print(f"   ✓ {len(parsed['samples'])} muestras procesadas")
            
        except Exception as e:
            print(f"   ✗ Error procesando {file}: {str(e)}")
            db.rollback()
            continue

    save_processed(processed)

    if nuevos > 0:
        print(f"\n✔ {nuevos} PDFs procesados y combinados generados en '{CARPETA_OUTPUTS}'")
    else:
        print("\n✔ No hay PDFs nuevos para procesar.")

    db.close()
    print("\n✔ Proceso completo.\n")

# ================= SCHEDULER =================

if __name__ == "__main__":
    init_db()
    
    # Programar ejecución cada 12 horas
    schedule.every(12).hours.do(process_pdfs)

    print("🚀 SERVICIO DE PROCESAMIENTO DE PDFS INICIADO")
    print("📁 Monitoreando carpeta:", PDF_FOLDER)
    print("📂 Salida de PDFs combinados:", CARPETA_OUTPUTS)
    print("⏰ Ejecutándose cada 12 horas")
    print("="*60)
    
    # Primera ejecución
    process_pdfs()

    # Bucle principal
    while True:
        schedule.run_pending()
        time.sleep(30)