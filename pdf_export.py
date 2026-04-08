import os
import shutil
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from models import Rad


# ===== COLORES INSTITUCIONALES =====
COLOR_PRIMARIO = colors.HexColor("#06ad57")   # verde
COLOR_SECUNDARIO = colors.HexColor("#003366") # azul
COLOR_GRIS = colors.HexColor("#F2F2F2")


# ===== CONFIG =====
CARPETA_ENTRADA = "entrada"
CARPETA_PROCESADOS = "procesados"
CARPETA_ERROR = "error"
CARPETA_LOGS = "logs"
CARPETA_OUTPUTS = "outputs"

LOG_PROCESADOS = os.path.join(CARPETA_LOGS, "procesados.txt")
LOG_AUDITORIA = os.path.join(CARPETA_LOGS, "auditoria.log")


# ===== SETUP =====
def asegurar_carpetas():
    for c in [CARPETA_ENTRADA, CARPETA_PROCESADOS, CARPETA_ERROR, CARPETA_LOGS, CARPETA_OUTPUTS]:
        os.makedirs(c, exist_ok=True)


def log(msg):
    with open(LOG_AUDITORIA, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {msg}\n")


def ya_procesado(nombre):
    if not os.path.exists(LOG_PROCESADOS):
        return False
    with open(LOG_PROCESADOS, "r") as f:
        return nombre in f.read().splitlines()


def registrar(nombre):
    with open(LOG_PROCESADOS, "a") as f:
        f.write(nombre + "\n")


# ===== HEADER INSTITUCIONAL =====
def header(canvas, doc):
    canvas.saveState()
    width, height = landscape(letter)

    canvas.setStrokeColor(COLOR_PRIMARIO)
    canvas.setLineWidth(2)
    canvas.line(30, height - 90, width - 30, height - 90)

    canvas.setFont("Helvetica-Bold", 13)
    canvas.setFillColor(COLOR_SECUNDARIO)
    canvas.drawRightString(
        width - 30,
        height - 50,
        "REPORTE DE RESULTADOS DE LABORATORIO"
    )

    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.black)
    canvas.drawRightString(width - 30, 20, f"Página {doc.page}")

    canvas.restoreState()


# ===== GENERAR PDF RECOMENDACIONES =====
def generar_pdf_recomendaciones(db, prefijo):
    styles = getSampleStyleSheet()

    # estilos personalizados
    styles.add(ParagraphStyle(
        name="TituloVerde",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=COLOR_PRIMARIO,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name="Subtitulo",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=COLOR_SECUNDARIO,
    ))

    rads = db.query(Rad).order_by(Rad.id).all()
    if not rads:
        return None

    nombre_temp = f"{prefijo}_recomendaciones.pdf"
    ruta = os.path.join(CARPETA_OUTPUTS, nombre_temp)

    doc = SimpleDocTemplate(
        ruta,
        pagesize=landscape(letter),
        leftMargin=30,
        rightMargin=30,
        topMargin=100,
        bottomMargin=40
    )

    elements = []

    for rad in rads:
        elements.append(
            Paragraph(f"RAD: {rad.rad_code}", styles["TituloVerde"])
        )

        for s in rad.samples:
            elements.append(
                Paragraph(f"Código Lab: {s.code}", styles["Subtitulo"])
            )
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

            elements.append(
                Paragraph("Recomendaciones técnicas:", styles["Subtitulo"])
            )
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(texto, styles["Normal"]))
            elements.append(Spacer(1, 20))

        elements.append(PageBreak())

    doc.build(elements, onFirstPage=header, onLaterPages=header)

    return ruta


# ===== UNIR PDFs =====
def unir_pdfs(pdf1, pdf2, salida):
    writer = PdfWriter()

    for pdf in [pdf1, pdf2]:
        reader = PdfReader(pdf)
        for page in reader.pages:
            writer.add_page(page)

    with open(salida, "wb") as f:
        writer.write(f)


# ===== AGRUPAR =====
def agrupar():
    archivos = [f for f in os.listdir(CARPETA_ENTRADA) if f.lower().endswith(".pdf")]
    grupos = {}

    for f in archivos:
        prefijo = f[:10]
        grupos.setdefault(prefijo, []).append(f)

    return grupos


# ===== PROCESO =====
def procesar(db):
    asegurar_carpetas()
    grupos = agrupar()

    for prefijo, archivos in grupos.items():

        original = None

        for f in archivos:
            if "con_resultados" not in f.lower():
                original = f

        if not original:
            continue

        if ya_procesado(original):
            log(f"SKIP: {original}")
            continue

        try:
            ruta_original = os.path.join(CARPETA_ENTRADA, original)

            pdf_reco = generar_pdf_recomendaciones(db, prefijo)

            if not pdf_reco:
                log(f"ERROR: sin recomendaciones {original}")
                continue

            salida = os.path.join(CARPETA_PROCESADOS, original)

            unir_pdfs(ruta_original, pdf_reco, salida)

            registrar(original)

            shutil.move(ruta_original, os.path.join(CARPETA_PROCESADOS, original))

            log(f"OK: {original}")

        except Exception as e:
            log(f"ERROR: {original} - {str(e)}")
            shutil.move(ruta_original, os.path.join(CARPETA_ERROR, original))


# ===== MAIN =====
if __name__ == "__main__":
    from database import SessionLocal

    db = SessionLocal()
    procesar(db)
    db.close()
