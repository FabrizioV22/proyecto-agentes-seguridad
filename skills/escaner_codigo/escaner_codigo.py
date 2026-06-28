import sys
import subprocess  # nosec B404
import re
import os
import json

def analizar_codigo_python(ruta_archivo):
    """
    Ejecuta Bandit sobre el archivo o carpeta de Python para detectar vulnerabilidades comunes.
    """
    try:
        # Comando base
        cmd = ["bandit", "-r", ruta_archivo, "-f", "txt"]
        
        # Intentamos usar el binario de venv si existe en el proyecto
        venv_path = "/root/proyecto-agentes-seguridad/venv-seguridad/bin/bandit"
        if os.path.exists(venv_path):
            cmd[0] = venv_path

        resultado = subprocess.run(  # nosec B603
            cmd,
            capture_output=True, text=True, timeout=60
        )
        return {
            "herramienta": "bandit",
            "lenguaje": "python",
            "stdout": resultado.stdout,
            "stderr": resultado.stderr,
            "status": "success"
        }
    except Exception as e:
        return {"error": f"Error al ejecutar Bandit: {str(e)}", "status": "error"}

def analizar_codigo_matlab(ruta_archivo):
    """
    Realiza un análisis léxico-semántico estático de un archivo .m de MATLAB.
    """
    if not os.path.exists(ruta_archivo):
        return {"error": f"El archivo {ruta_archivo} no existe.", "status": "error"}
    
    patrones_riesgo = {
        r'\beval\s*\(': "Uso de 'eval()': Inyección potencial de código si recibe entradas de usuario.",
        r'\bevalc\s*\(': "Uso de 'evalc()': Inyección potencial de código.",
        r'\bsystem\s*\(': "Uso de 'system()': Ejecución de comandos del sistema operativo (Command Injection).",
        r'\bunix\s*\(': "Uso de 'unix()': Ejecución de comandos en entornos Unix (Command Injection).",
        r'\bdos\s*\(': "Uso de 'dos()': Ejecución de comandos en entornos Windows (Command Injection).",
        r'\bpopen\s*\(': "Uso de 'popen()': Apertura de tuberías de sistema.",
        r'\binput\s*\(\s*\'[^\']*\'\s*,\s*\'s\'\s*\)': "Lectura directa de entrada de usuario sin sanitizar.",
    }
    
    hallazgos = []
    try:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
            lineas = f.readlines()
            
        for num_linea, line in enumerate(lineas, 1):
            linea_limpia = line.split('%')[0]  # Ignorar comentarios
            for patron, desc in patrones_riesgo.items():
                if re.search(patron, linea_limpia):
                    hallazgos.append({
                        "linea": num_linea,
                        "codigo": line.strip(),
                        "detalle": desc
                    })
        return {
            "herramienta": "analisis_estatico_matlab",
            "lenguaje": "matlab",
            "hallazgos": hallazgos,
            "status": "success"
        }
    except Exception as e:
        return {"error": f"Error al leer archivo MATLAB: {str(e)}", "status": "error"}

def escanear(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        return json.dumps({"error": f"El archivo o ruta '{ruta_archivo}' no existe.", "status": "error"})
        
    if os.path.isdir(ruta_archivo):
        resultados = []
        for raiz, dirs, archivos in os.walk(ruta_archivo):
            for archivo in archivos:
                ruta_completa = os.path.join(raiz, archivo)
                if archivo.endswith('.py'):
                    resultados.append(analizar_codigo_python(ruta_completa))
                elif archivo.endswith('.m'):
                    resultados.append(analizar_codigo_matlab(ruta_completa))
        return json.dumps({"directorio": ruta_archivo, "resultados": resultados, "status": "success"}, ensure_ascii=False)
    
    if ruta_archivo.endswith('.py'):
        res = analizar_codigo_python(ruta_archivo)
    elif ruta_archivo.endswith('.m'):
        res = analizar_codigo_matlab(ruta_archivo)
    else:
        res = {"error": f"Extensión no soportada para análisis estático en '{ruta_archivo}'", "status": "error"}
        
    return json.dumps(res, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
        print(escanear(ruta))
    else:
        print(json.dumps({"error": "No se especificó la ruta del archivo o carpeta.", "status": "error"}))
