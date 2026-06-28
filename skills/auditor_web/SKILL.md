---
name: auditor_web
description: Ejecuta SQLMap para detectar vulnerabilidades de inyección SQL en aplicaciones web con escaneo de formularios y crawling automático.
user-invocable: true
---

# Auditor SQLmap (auditor_web)

Esta herramienta ejecuta SQLMap de forma automatizada para detectar vulnerabilidades de inyección SQL en aplicaciones web. Realiza escaneo de formularios y crawling básico con configuración segura y controlada.

## INVOCACIÓN OBLIGATORIA — copia exacta sin modificar formato:
{"function":"exec","args":{"command":"python3 /root/.openclaw/skills/auditor_web/sqlmap_runner.py 'URL_OBJETIVO'","timeout":300}}

Sustituye 'URL_OBJETIVO' por la URL completa del objetivo. Usa ÚNICAMENTE comillas simples (') para envolver los argumentos dentro del comando para evitar romper la estructura del JSON en la terminal.