---
name: detector_secretos
description: Escanea repositorios Git y directorios de código en busca de API Keys, tokens, contraseñas, claves privadas SSH/RSA y credenciales expuestas usando Gitleaks.
user-invocable: true
---

# Módulo de Análisis de Secretos y Fugas de Credenciales (detector_secretos)

Esta herramienta escanea repositorios Git o directorios de código fuente en busca de secretos expuestos: API Keys, tokens de GitHub/AWS/GCP, contraseñas hardcodeadas, claves privadas SSH y cualquier credencial que se haya quedado en el código por error. Utiliza Gitleaks, herramienta líder en la industria para prevención de fugas de credenciales en pipelines DevSecOps.

**Modos de operación:**
- **Modo Git:** Si el directorio objetivo contiene un repositorio `.git`, escanea el historial completo de commits buscando secretos que se hayan subido en cualquier momento (incluso si fueron borrados después).
- **Modo Directorio:** Si no es un repo Git, escanea todos los archivos del directorio de forma recursiva.

**Cuándo usarla:** Ejecutar ANTES de hacer un commit o push a un repositorio remoto, o cuando se sospeche que credenciales fueron expuestas en el código fuente.

## INVOCACIÓN OBLIGATORIA — copia exacta sin modificar formato:
{"function":"exec","args":{"command":"python3 /root/.openclaw/skills/detector_secretos/detector_secretos.py 'RUTA_DEL_REPOSITORIO_O_DIRECTORIO'"}}

Sustituye 'RUTA_DEL_REPOSITORIO_O_DIRECTORIO' por la ruta absoluta del proyecto o directorio a escanear (ej. '/root/proyecto-agentes-seguridad'). Usa ÚNICAMENTE comillas simples (') para envolver los argumentos dentro del comando para evitar romper la estructura del JSON en la terminal.
