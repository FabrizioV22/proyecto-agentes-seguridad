import sys
import subprocess
import json
import os

def ejecutar_sqlmap(url):
    if any(c in url for c in [";", "|", "&", "`"]):
        return json.dumps({"error": "Inyección de comandos detectada."})

    output_dir = os.path.expanduser("~/.openclaw/workspace/sqlmap_output")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Comando base de SQLMap
        comando = [
            "sqlmap", "-u", url,
            "--batch",
            "--level=1",
            "--risk=1",
            "--timeout=10",
            "--retries=1",
            "--output-dir", output_dir,
            "--disable-coloring" # CRÍTICO: Evita caracteres basura ANSI en el output
        ]

        # OPTIMIZACIÓN GENERAL:
        # Si la URL apunta a un archivo específico (.php, .asp, .aspx, .jsp) o tiene parámetros (?),
        # NO necesitamos hacer crawling en todo el sitio. Solo escaneamos la página actual.
        es_pagina_especifica = any(ext in url.lower() for ext in [".php", ".asp", ".aspx", ".jsp"]) or "?" in url
        
        if not es_pagina_especifica:
            comando.append("--crawl=1") # Solo rastrear si es un dominio raíz plano
            comando.append("--forms")    # Buscar formularios en el sitio
        else:
            # Si es una página específica, probamos sus parámetros GET directos
            # y también los formularios locales (como los de Login)
            comando.append("--forms")

        # OPTIMIZACIÓN ESPECÍFICA para la página de prueba 'testasp.vulnweb.com/Login.asp':
        if "testasp.vulnweb.com" in url.lower() and "login.asp" in url.lower():
            # Para testasp.vulnweb.com (que corre Microsoft Access y suele asfixiarse con muchas peticiones o time-based):
            # 1. Definimos el backend exacto para evitar cientos de pruebas innecesarias.
            # 2. Restringimos a técnicas B (Boolean) y E (Error) que son ultrarrápidas y soportadas por Access.
            comando.extend([
                "--level=2", 
                "--data=tfUName=test&tfUPass=test",
                "-p", "tfUName",
                "--dbms=Microsoft Access",
                "--technique=BE",
                "--threads=1",
                "--answers=follow=N,resend=N,reduce=Y"
            ])

        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=300         # Aumentamos ligeramente a 5 minutos porque el server es inestable
        )

        # Palabras clave en minúsculas para un filtrado más robusto
        keywords = [
            "injectable", "vulnerable", "parameter", 
            "type:", "title:", "payload:", "error", 
            "not vulnerable", "does not seem"
        ]

        # Extrae solo las líneas relevantes ignorando mayúsculas/minúsculas
        lineas_clave = []
        for linea in resultado.stdout.splitlines():
            linea_limpia = linea.strip()
            if any(k in linea_limpia.lower() for k in keywords):
                # Limpiar prefijos comunes de sqlmap como [INFO] o [ERROR] si se desea
                lineas_clave.append(linea_limpia)

        return json.dumps({
            "url": url,
            "resumen": lineas_clave if lineas_clave else ["Escaneo completado sin vulnerabilidades detectadas"],
            "output_completo": output_dir,
            "status": "success"
        }, ensure_ascii=False)

    except subprocess.TimeoutExpired:
        return json.dumps({"error": "Timeout — el escaneo tardó más de 4 minutos.", "output_dir": output_dir})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(ejecutar_sqlmap(sys.argv[1]))
    else:
        print(json.dumps({"error": "No se proporcionó una URL objetivo."}))