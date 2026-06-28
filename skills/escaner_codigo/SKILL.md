---
name: escaner_codigo
description: Analiza la seguridad de archivos de código Python y MATLAB/Octave buscando inyecciones, funciones inseguras (eval/system) y fallos de lógica con Bandit y análisis estático.
user-invocable: true
---

# Auditor de Código Estático (Python y MATLAB) (escaner_codigo)

Esta herramienta analiza la seguridad de archivos de código fuente Python (.py) y MATLAB/Octave (.m) en busca de inyecciones de comandos, funciones inseguras (eval/system) y fallos de lógica.

## INVOCACIÓN OBLIGATORIA — copia exacta sin modificar formato:
{"function":"exec","args":{"command":"python3 /root/.openclaw/skills/escaner_codigo/escaner_codigo.py 'RUTA_DEL_ARCHIVO_O_CARPETA'"}}

Sustituye 'RUTA_DEL_ARCHIVO_O_CARPETA' por la ruta absoluta del archivo o directorio a analizar. Usa ÚNICAMENTE comillas simples (') para envolver los argumentos dentro del comando para evitar romper la estructura del JSON en la terminal.
