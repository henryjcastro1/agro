import os
import re

def fix_imports_in_file(filepath):
    """Corrige imports relativos en archivos dentro de src/"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Eliminar 'src.' de los imports
        content = re.sub(r'from src\.database\.', 'from database.', content)
        content = re.sub(r'from src\.core\.', 'from core.', content)
        content = re.sub(r'from src\.export\.', 'from export.', content)
        content = re.sub(r'from src\.gui\.', 'from gui.', content)
        
        content = re.sub(r'import src\.database\.', 'import database.', content)
        content = re.sub(r'import src\.core\.', 'import core.', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Corregido: {filepath}")
            return True
    except Exception as e:
        print(f"✗ Error en {filepath}: {e}")
    return False

# Recorrer todos los archivos Python en src/
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            fix_imports_in_file(filepath)

print("\n✅ ¡Todos los imports han sido corregidos!")