# pdf_recomendaciones_processor.py
import os
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from PyPDF2 import PdfReader, PdfWriter

def extraer_recomendaciones_de_pdf(ruta_pdf):
    """
    Extrae las recomendaciones de un PDF generado por tu sistema
    """
    recomendaciones = []
    doc = fitz.open(ruta_pdf)
    
    for pagina in doc:
        texto = pagina.get_text()
        if "Recomendaciones IA:" in texto:
            partes = texto.split("Recomendaciones IA:")
            if len(partes) > 1:
                rec_texto = partes[1].strip()
                recomendaciones.append(rec_texto)
    
    doc.close()
    return recomendaciones

def crear_pdf_recomendaciones(recomendaciones, output_path):
    """
    Crea un PDF con solo las recomendaciones
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=30,
        rightMargin=30,
        topMargin=130,
        bottomMargin=40
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(
        Paragraph(
            "<b>RECOMENDACIONES DE ANÁLISIS</b>",
            styles["Heading1"]
        )
    )
    elements.append(Spacer(1, 20))
    
    for i, rec in enumerate(recomendaciones, 1):
        elements.append(
            Paragraph(
                f"<b>Recomendación {i}:</b>",
                styles["Heading3"]
            )
        )
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(
                rec.replace('\n', '<br/>'),
                styles["Normal"]
            )
        )
        elements.append(Spacer(1, 20))
    
    def draw_simple_header(canvas, doc):
        canvas.saveState()
        width, height = landscape(letter)
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawRightString(
            width - 30,
            height - 40,
            "RECOMENDACIONES"
        )
        canvas.line(30, height - 90, width - 30, height - 90)
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(
            width - 30,
            20,
            f"Página {doc.page}"
        )
        canvas.restoreState()
    
    doc.build(elements, onFirstPage=draw_simple_header, onLaterPages=draw_simple_header)

def combinar_pdfs(pdf_original, pdf_recomendaciones, output_path):
    """
    Combina dos PDFs en uno solo
    """
    pdf_final = PdfWriter()
    
    with open(pdf_original, 'rb') as file:
        pdf1 = PdfReader(file)
        for pagina in pdf1.pages:
            pdf_final.add_page(pagina)
    
    with open(pdf_recomendaciones, 'rb') as file:
        pdf2 = PdfReader(file)
        for pagina in pdf2.pages:
            pdf_final.add_page(pagina)
    
    with open(output_path, 'wb') as output_file:
        pdf_final.write(output_file)

def procesar_pdfs_recomendaciones(carpeta_origen="outputs", carpeta_destino="outputs_procesados"):
    """
    Procesa los PDFs para extraer recomendaciones
    """
    os.makedirs(carpeta_destino, exist_ok=True)
    carpeta_recomendaciones = os.path.join(carpeta_destino, "solo_recomendaciones")
    carpeta_combinados = os.path.join(carpeta_destino, "combinados")
    os.makedirs(carpeta_recomendaciones, exist_ok=True)
    os.makedirs(carpeta_combinados, exist_ok=True)
    
    pdfs = [f for f in os.listdir(carpeta_origen) if f.endswith('.pdf')]
    
    if not pdfs:
        print("📁 No hay PDFs para procesar en outputs/")
        return
    
    print(f"\n📁 Procesando {len(pdfs)} PDFs para extraer recomendaciones...")
    
    for pdf_file in pdfs:
        ruta_pdf = os.path.join(carpeta_origen, pdf_file)
        nombre_base = os.path.splitext(pdf_file)[0]
        
        recomendaciones = extraer_recomendaciones_de_pdf(ruta_pdf)
        
        if recomendaciones:
            # Crear PDF solo con recomendaciones
            ruta_recomendaciones = os.path.join(
                carpeta_recomendaciones, 
                f"{nombre_base}_RECOMENDACIONES.pdf"
            )
            crear_pdf_recomendaciones(recomendaciones, ruta_recomendaciones)
            
            # Combinar PDFs
            ruta_combinado = os.path.join(
                carpeta_combinados, 
                f"{nombre_base}_COMPLETO.pdf"
            )
            combinar_pdfs(ruta_pdf, ruta_recomendaciones, ruta_combinado)
            
            print(f"  ✓ {pdf_file} → {len(recomendaciones)} recomendaciones extraídas")
        else:
            print(f"  ⚠ {pdf_file} → Sin recomendaciones")
    
    print(f"✅ PDFs procesados guardados en: {carpeta_destino}")