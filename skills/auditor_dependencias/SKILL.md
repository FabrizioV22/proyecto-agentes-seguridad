---
name: auditor_dependencias
description: Analiza requirements.txt en busca de vulnerabilidades CVE en librerías usando Safety.
user-invocable: true
---

# Módulo de Análisis de Dependencias y Vulnerabilidades de Terceros (SCA)

Este módulo revisa los archivos de requerimientos (como requirements.txt) para verificar si las librerías de terceros utilizadas tienen vulnerabilidades conocidas (CVEs). La herramienta base utilizada es Safety para entornos Python.

Cuando detecta una librería obsoleta o vulnerable, genera un reporte detallado con la recomendación y la lista de comandos para actualizar a una versión segura.

## INVOCACIÓN OBLIGATORIA — copia exacta sin modificar formato:
{"function":"exec","args":{"command":"python3 /root/.openclaw/skills/auditor_dependencias/auditor_dependencias.py 'TARGET'"}}

Sustituye 'TARGET' por la ruta absoluta al directorio del proyecto o al archivo requirements.txt. Usa ÚNICAMENTE comillas simples (') para envolver los argumentos dentro del comando para evitar romper la estructura del JSON en la terminal.
