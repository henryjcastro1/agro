from src.core.parser import parse_pdf

data = parse_pdf("pdfs/Ga F 97Sol.pdf")

print("RAD:", data["rad"])
print("Fecha:", data["fecha"])
print("Cliente:", data["cliente"])
print("\nMUESTRAS ENCONTRADAS:", len(data["samples"]))

for s in data["samples"]:
    print(s)
