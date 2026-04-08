import pdfplumber

with pdfplumber.open("pdfs/Ga F 97Sol.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        print("\n--- PAGINA", i+1, "---\n")
        print(page.extract_text())
