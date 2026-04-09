import pdfplumber
import re

def parse_pdf(path):
    data = {
        "rad": None,
        "cliente": None,
        "fecha": None,
        "samples": []
    }

    with pdfplumber.open(path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages)

        # ---------------------- RAD ----------------------
        rad = re.search(r"(RAD_[A-Z0-9_]+)", text)
        if rad:
            data["rad"] = rad.group(1)

        # ---------------------- CLIENTE ----------------------
        cliente = re.search(r"INFORME No\.[^\n]+\s+([A-Za-zÁÉÍÓÚÑ\s]+)", text)
        if cliente:
            data["cliente"] = cliente.group(1).strip()

        # ---------------------- FECHA ----------------------
        fecha = re.search(r"\d{4}-\d{2}-\d{2}", text)
        if fecha:
            data["fecha"] = fecha.group(0)

        # ---------------------- TABLA DE MUESTRAS ----------------------
        # REGEX SUPER TOLERANTE
        sample_pattern = re.compile(
            r"(LMPSA_\d+)\s+"
            r"No\s*indica\s*"
            r"([0-9.\-]+)\s+"        # ureico
            r"([0-9.\-]+)\s+"        # células
            r"([0-9.\-]+)\s+"        # grasa
            r"([0-9.\-]+)\s+"        # lactosa
            r"([0-9.\-]+)\s+"        # crioscópico
            r"([0-9.\-]+)\s+"        # proteína
            r"([0-9.\-]+)\s+"        # sólidos
            r"([0-9.\-]+)"           # mesófilas
        )

        for m in sample_pattern.finditer(text):
            data["samples"].append({
                "code": m.group(1),

                "n_ureico": float(m.group(2)),
                "celulas": int(float(m.group(3))),
                "grasa": m.group(4),
                "lactosa": m.group(5),
                "p_crioscopico": m.group(6),
                "proteina": m.group(7),
                "solidos": m.group(8),
                "mesofilas": int(float(m.group(9))),
            })

    return data
