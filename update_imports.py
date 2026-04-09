import os
import re

def update_imports_in_file(filepath):
    """Actualiza los imports en un archivo Python"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Patrones de reemplazo (de menor a mayor especificidad)
        replacements = [
            # Imports de modelos/db
            (r'from models import', 'from src.core.models import'),
            (r'from db import', 'from src.database.db import'),
            (r'from parser import', 'from src.core.parser import'),
            (r'from recommender import', 'from src.core.recommender import'),
            
            # Imports relativos a otros módulos
            (r'from excel_export import', 'from src.export.excel_export import'),
            (r'from pdf_export import', 'from src.export.pdf_export import'),
            (r'from gui_config_recomendaciones import', 'from src.gui.gui_config_recomendaciones import'),
            
            # Imports de procesador
            (r'from pdf_recomendaciones_processor import', 'from src.core.pdf_recomendaciones_processor import'),
            
            # Imports de scripts de BD
            (r'from init_db import', 'from src.database.init_db import'),
            (r'from debug_db import', 'from src.database.debug_db import'),
            
            # Imports absolutos (sin from)
            (r'^import models\b', 'import src.core.models'),
            (r'^import db\b', 'import src.database.db'),
            (r'^import parser\b', 'import src.core.parser'),
            (r'^import recommender\b', 'import src.core.recommender'),
        ]
        
        for old, new in replacements:
            content = re.sub(old, new, content, flags=re.MULTILINE)
        
        # Solo escribir si hubo cambios
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Actualizado: {filepath}")
            return True
        else:
            print(f"  Sin cambios: {filepath}")
            return False
            
    except Exception as e:
        print(f"✗ Error en {filepath}: {e}")
        return False

# Lista de archivos a procesar
files_to_update = [
    'src/main.py',
    'src/core/parser.py',
    'src/core/recommender.py',
    'src/core/models.py',
    'src/core/pdf_recomendaciones_processor.py',
    'src/database/db.py',
    'src/database/init_db.py',
    'src/database/debug_db.py',
    'src/export/excel_export.py',
    'src/gui/gui_config_recomendaciones.py',
    'scripts/launch_gui.py',
    'tests/test_parser.py',
    'tests/test_raw_text.py',
]

print("Actualizando imports...")
print("-" * 40)

updated_count = 0
for filepath in files_to_update:
    if os.path.exists(filepath):
        if update_imports_in_file(filepath):
            updated_count += 1
    else:
        print(f"✗ No encontrado: {filepath}")

print("-" * 40)
print(f"Actualizados: {updated_count} archivos")

# También verificar archivos .py en config (si hay)
config_files = [f for f in os.listdir('.') if f.endswith('.py') and f not in files_to_update]
if config_files:
    print(f"\nArchivos adicionales encontrados: {config_files}")