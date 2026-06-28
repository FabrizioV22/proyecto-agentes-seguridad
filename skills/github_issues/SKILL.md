---
name: github_issues
description: Crea reportes de vulnerabilidad como GitHub Issues automáticamente cuando se detectan fallos de seguridad con Bandit, Nmap o análisis estático de código.
user-invocable: true
---

# Creador de Reportes DevSecOps (GitHub Issues)

Esta herramienta automatiza la creación de reportes de vulnerabilidad (Issues) en el repositorio de GitHub de forma remota y absoluta. Úsala INMEDIATAMENTE cuando encuentres una vulnerabilidad o fallo crítico usando herramientas como Bandit, Nmap o análisis estático de código.

## INVOCACIÓN OBLIGATORIA — copia exacta sin modificar formato:
{"function":"exec","args":{"command":"python3 /root/.openclaw/skills/github_issues/crear_issue.py 'TITULO_BREVE' 'DESCRIPCION_TECNICA'"}}

Sustituye 'TITULO_BREVE' por un resumen claro del fallo y 'DESCRIPCION_TECNICA' por el detalle del hallazgo y la solución recomendada. NUNCA uses comillas dobles (") dentro de los argumentos, usa ÚNICAMENTE comillas simples (') para evitar romper la estructura del JSON en la terminal.