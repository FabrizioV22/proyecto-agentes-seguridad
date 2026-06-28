import sys
import subprocess
import json
import os
import re

def validar_ruta(ruta):
    """
    Valida que la ruta proporcionada sea segura y exista en el sistema.
    """
    ruta = ruta.strip()
    # Rechazar caracteres peligrosos para inyección de comandos
    if any(c in ruta for c in [";", "|", "&", "`", "$", "(", ")", "{", "}"]):
        return False
    if not os.path.exists(ruta):
        return False
    return True

def ejecutar_safety(ruta_objetivo):
    if not validar_ruta(ruta_objetivo):
        return json.dumps({
            "error": f"La ruta '{ruta_objetivo}' no es válida o no existe.",
            "status": "error"
        }, ensure_ascii=False)

    # Si es un directorio, buscar requirements.txt
    req_file = ruta_objetivo
    if os.path.isdir(ruta_objetivo):
        req_file = os.path.join(ruta_objetivo, "requirements.txt")
        if not os.path.exists(req_file):
            return json.dumps({
                "error": f"No se encontró 'requirements.txt' en el directorio {ruta_objetivo}.",
                "status": "error"
            }, ensure_ascii=False)

    try:
        comando = [
            "safety", "check",
            "-r", req_file,
            "--output", "json"
        ]

        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=60
        )

        # Parsear JSON. A veces safety añade texto extra de deprecación, así que buscamos el bloque JSON.
        salida = resultado.stdout
        # Extraer JSON usando regex (buscando desde { hasta })
        match = re.search(r'(\{.*\})', salida, re.DOTALL)
        if not match:
            if "No vulnerabilities found" in salida or not salida.strip():
                 return json.dumps({
                    "ruta": req_file,
                    "total_vulnerabilidades": 0,
                    "hallazgos": [],
                    "veredicto": "LIMPIO — No se detectaron vulnerabilidades en las dependencias.",
                    "status": "success"
                }, ensure_ascii=False)
            return json.dumps({
                "error": "No se pudo parsear el output de Safety.",
                "raw_output": salida[:500],
                "status": "error"
            }, ensure_ascii=False)

        json_str = match.group(1)
        data = json.loads(json_str)

        vulnerabilidades = data.get("vulnerabilities", [])
        if not vulnerabilidades:
            return json.dumps({
                "ruta": req_file,
                "total_vulnerabilidades": 0,
                "hallazgos": [],
                "veredicto": "LIMPIO — No se detectaron vulnerabilidades en las dependencias.",
                "status": "success"
            }, ensure_ascii=False)

        hallazgos_formateados = []
        comandos_actualizacion = set()

        for v in vulnerabilidades:
            paquete = v.get("package_name")
            hallazgo = {
                "paquete": paquete,
                "version_actual": v.get("analyzed_version"),
                "id_vulnerabilidad": v.get("vulnerability_id"),
                "cve": v.get("CVE"),
                "descripcion": v.get("advisory"),
                "severidad": v.get("severity", "ALTA")
            }
            hallazgos_formateados.append(hallazgo)
            comandos_actualizacion.add(f"pip install --upgrade {paquete}")

        return json.dumps({
            "ruta": req_file,
            "total_vulnerabilidades": len(hallazgos_formateados),
            "hallazgos": hallazgos_formateados,
            "veredicto": f"ALERTA — Se detectaron {len(hallazgos_formateados)} vulnerabilidad(es) en librerías de terceros.",
            "recomendacion": "Actualiza las librerías afectadas usando los comandos proporcionados.",
            "comandos_actualizacion": list(comandos_actualizacion),
            "status": "success"
        }, ensure_ascii=False)

    except FileNotFoundError:
        return json.dumps({
            "error": "La herramienta 'safety' no está instalada en el sistema. Instálala con 'pip install safety'.",
            "status": "error"
        }, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        return json.dumps({
            "error": "Timeout — el escaneo de dependencias tardó demasiado.",
            "status": "error"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        }, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
        print(ejecutar_safety(ruta))
    else:
        print(json.dumps({
            "error": "No se proporcionó la ruta del archivo requirements.txt o del directorio.",
            "uso": "python3 auditor_dependencias.py '/ruta/al/proyecto'",
            "status": "error"
        }, ensure_ascii=False))
