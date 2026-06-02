import subprocess
import json
import sys

def escanear_inyeccion_sql(url_objetivo):
    print(f"[*] Lanzando SQLmap sobre: {url_objetivo}")
    try:
        # --batch hace que SQLmap responda "Y" a todo por defecto sin detenerse
        comando = ["sqlmap", "-u", url_objetivo, "--batch", "--level=1", "--risk=1"]
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=120)
        
        # Filtramos la salida para no saturar la memoria del LLM
        lineas_importantes = []
        for linea in resultado.stdout.split('\n'):
            if "Parameter:" in linea or "Type:" in linea or "Title:" in linea or "Payload:" in linea or "vulnerable" in linea.lower():
                lineas_importantes.append(linea)
                
        if lineas_importantes:
            return "\n".join(lineas_importantes)
        else:
            return "No se encontraron vulnerabilidades SQLi evidentes con este escaneo básico."
            
    except subprocess.TimeoutExpired:
        return "El escaneo de SQLmap superó el tiempo límite."
    except Exception as e:
        return f"Error al ejecutar SQLmap: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(escanear_inyeccion_sql(sys.argv[1]))
    else:
        print("Proporciona una URL válida.")
