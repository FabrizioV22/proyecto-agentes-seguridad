import subprocess
import json
import sys

def escanear_puertos(target):
    print(f"[*] Iniciando escaneo de seguridad sobre: {target}")
    try:
        # Ejecución nativa y segura (evita inyección de comandos en el script)
        comando = ["nmap", "-sV", "--top-ports", "50", target]
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=60)
        
        if resultado.returncode == 0:
            return resultado.stdout
        else:
            return f"Error en la ejecución de Nmap: {resultado.stderr}"
    except Exception as e:
        return f"Excepción al ejecutar el escaneo: {str(e)}"

if __name__ == "__main__":
    objetivo = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    print(escanear_puertos(objetivo))
