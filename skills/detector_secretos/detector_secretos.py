import sys
import subprocess
import json
import os
import tempfile

def validar_ruta(ruta):
    """
    Valida que la ruta proporcionada sea segura y exista en el sistema.
    Previene path traversal e inyección de comandos.
    """
    ruta = ruta.strip()
    # Rechazar caracteres peligrosos para inyección de comandos
    if any(c in ruta for c in [";", "|", "&", "`", "$", "(", ")", "{", "}"]):
        return False
    # Verificar que la ruta exista
    if not os.path.exists(ruta):
        return False
    return True

def ejecutar_gitleaks(ruta_objetivo):
    """
    Ejecuta Gitleaks sobre un directorio o repositorio Git para detectar
    secretos expuestos (API Keys, tokens, contraseñas, claves privadas).
    Retorna un JSON estructurado con los hallazgos.
    """
    if not validar_ruta(ruta_objetivo):
        return json.dumps({
            "error": f"La ruta '{ruta_objetivo}' no es válida o no existe en el sistema.",
            "status": "error"
        }, ensure_ascii=False)

    # Determinar si el objetivo es un repositorio Git o un directorio plano
    es_repo_git = os.path.isdir(os.path.join(ruta_objetivo, ".git"))

    # Crear archivo temporal para el reporte JSON de Gitleaks
    reporte_tmp = tempfile.mktemp(suffix=".json", prefix="gitleaks_report_")

    try:
        comando = [
            "gitleaks",
            "detect",
            "--source", ruta_objetivo,
            "--report-format", "json",
            "--report-path", reporte_tmp,
            "--no-banner",
            "--exit-code", "0"
        ]
        
        if not es_repo_git:
            comando.append("--no-git")

        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Leer el reporte JSON generado por Gitleaks
        hallazgos_raw = []
        if os.path.exists(reporte_tmp):
            try:
                with open(reporte_tmp, "r", encoding="utf-8") as f:
                    contenido = f.read().strip()
                    if contenido:
                        hallazgos_raw = json.loads(contenido)
            except (json.JSONDecodeError, IOError):
                pass
            finally:
                os.remove(reporte_tmp)
        
        if not hallazgos_raw:
            return json.dumps({
                "ruta": ruta_objetivo,
                "modo": "git (historial de commits)" if es_repo_git else "directorio (archivos actuales)",
                "total_secretos": 0,
                "hallazgos": [],
                "veredicto": "LIMPIO — No se detectaron secretos expuestos.",
                "status": "success"
            }, ensure_ascii=False)

        # Formatear hallazgos para el agente de IA
        hallazgos_formateados = []
        for h in hallazgos_raw:
            hallazgo = {
                "regla": h.get("RuleID", "desconocida"),
                "descripcion": h.get("Description", "Sin descripción"),
                "archivo": h.get("File", "desconocido"),
                "linea_inicio": h.get("StartLine", 0),
                "linea_fin": h.get("EndLine", 0),
                "fragmento": h.get("Match", "")[:200],
                "commit": h.get("Commit", "N/A"),
                "autor": h.get("Author", "N/A"),
                "fecha": h.get("Date", "N/A"),
                "severidad": "CRITICA"
            }
            hallazgos_formateados.append(hallazgo)

        return json.dumps({
            "ruta": ruta_objetivo,
            "modo": "git (historial de commits)" if es_repo_git else "directorio (archivos actuales)",
            "total_secretos": len(hallazgos_formateados),
            "hallazgos": hallazgos_formateados,
            "veredicto": f"ALERTA — Se detectaron {len(hallazgos_formateados)} secreto(s) expuesto(s). Requiere acción inmediata.",
            "recomendacion": "1) Revocar las credenciales comprometidas de inmediato. 2) Eliminar del historial Git con 'git filter-branch' o BFG Repo-Cleaner. 3) Rotar todas las claves afectadas en los servicios correspondientes. 4) Agregar los patrones a .gitignore y configurar un hook pre-commit con Gitleaks.",
            "status": "success"
        }, ensure_ascii=False)

    except FileNotFoundError:
        return json.dumps({
            "error": "La herramienta 'gitleaks' no está instalada en el sistema.",
            "instalacion": "Descargar desde: https://github.com/gitleaks/gitleaks/releases",
            "status": "error"
        }, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        return json.dumps({
            "error": "Timeout — el escaneo tardó más de 2 minutos. Intenta con un directorio más pequeño o menos profundo.",
            "status": "error"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        }, ensure_ascii=False)
    finally:
        # Limpieza del archivo temporal por si acaso
        if os.path.exists(reporte_tmp):
            os.remove(reporte_tmp)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # En caso de que el agente de IA alucine argumentos (ej. pasando la ruta de gitleaks o palabras clave como 'detect')
        # Buscamos el argumento que sea la ruta objetivo real.
        ruta = None
        for arg in sys.argv[1:]:
            # Omitimos flags
            if arg.startswith("-"):
                continue
            # Omitimos subcomandos comunes de gitleaks
            if arg in ["detect", "git", "dir", "scan"]:
                continue
            # Omitimos si apunta al binario de gitleaks
            if "gitleaks" in arg.lower() and os.path.isfile(arg) and os.access(arg, os.X_OK):
                continue
            # Si el argumento existe en el sistema, lo tomamos como la ruta objetivo
            if os.path.exists(arg):
                ruta = arg
                break
        
        # Fallback al primer argumento si no encontramos nada robusto
        if not ruta:
            ruta = sys.argv[1]

        print(ejecutar_gitleaks(ruta))
    else:
        print(json.dumps({
            "error": "No se proporcionó la ruta del directorio o repositorio a escanear.",
            "uso": "python3 detector_secretos.py '/ruta/al/proyecto'",
            "status": "error"
        }, ensure_ascii=False))
