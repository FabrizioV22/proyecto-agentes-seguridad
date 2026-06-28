import sys
import subprocess  # nosec B404
import json
import re

def validar_target(target):
    """
    Valida el target para evitar inyección de comandos en el shell
    y verificar que sea un dominio o IP válidos.
    """
    # Expresión regular básica para IP o dominio
    patron = r'^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$'
    # Permitir también IPv4 simple
    patron_ip = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    
    target = target.strip()
    if re.match(patron, target) or re.match(patron_ip, target):
        return True
    return False

def ejecutar_escaneo(target):
    if not validar_target(target):
        return json.dumps({
            "error": "El objetivo proporcionado no es un dominio o dirección IP válidos.",
            "status": "error"
        })
    
    try:
        # Ejecutamos Nmap de forma segura sin shell=True
        # Limitamos a los 50 puertos principales con detección de servicios (-sV)
        comando = ["nmap", "-sV", "--top-ports", "50", target]
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=60)  # nosec B603
        
        if resultado.returncode == 0:
            return json.dumps({
                "target": target,
                "stdout": resultado.stdout,
                "status": "success"
            }, ensure_ascii=False)
            
        return json.dumps({
            "target": target,
            "error": resultado.stderr,
            "status": "error"
        }, ensure_ascii=False)
        
    except FileNotFoundError:
        return json.dumps({
            "error": "La herramienta 'nmap' no está instalada en el sistema.",
            "status": "error"
        })
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        print(ejecutar_escaneo(target))
    else:
        print(json.dumps({
            "error": "No se proporcionó un objetivo (IP o dominio).",
            "status": "error"
        }))
