import os
from openpyxl import Workbook
from src.core.models import Rad


def export_to_excel(db, path="outputs/resultados.xlsx"):

    wb = Workbook()
    ws = wb.active
    ws.title = "Resultados LMPSA"

    ws.append([
        "RAD",
        "Muestra",
        "Parámetro",
        "Recomendaciones"
    ])

    rads = db.query(Rad).all()

    for rad in rads:
        for s in rad.samples:
            bloques = s.recomendaciones.split("\n\n")
            for bloque in bloques:
                lineas = bloque.strip().split("\n")
                if not lineas:
                    continue

                parametro = lineas[0]
                texto = " ".join(lineas[1:])

                ws.append([
                    rad.rad_code,
                    s.code,
                    parametro,
                    texto
                ])

    os.makedirs(os.path.dirname(path), exist_ok=True)
    wb.save(path)
    print(f"✔ Excel generado correctamente (consolidado): {path}")