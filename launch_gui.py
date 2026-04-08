# launch_gui.py
import subprocess
import sys

def main():
    print("Iniciando Configurador de Recomendaciones...")
    subprocess.run([sys.executable, "gui_config_recomendaciones.py"])

if __name__ == "__main__":
    main()