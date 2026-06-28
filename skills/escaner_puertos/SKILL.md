---
name: escaner_puertos
description: Escanea puertos abiertos y servicios en servidores usando Nmap para reconocimiento de red y superficie de ataque en auditorías de seguridad.
user-invocable: true
---

# Módulo de Reconocimiento de Red y Superficie de Ataque (escaner_puertos)

Esta herramienta automatiza la fase de reconocimiento (Reconnaissance) en una auditoría de seguridad. Permite realizar escaneos activos de infraestructura tanto en entornos locales (127.0.0.1) como en servidores públicos autorizados en la WAN (ej. scanme.nmap.org) utilizando Nmap.

## INVOCACIÓN OBLIGATORIA — copia exacta sin modificar formato:
{"function":"exec","args":{"command":"python3 /root/.openclaw/skills/escaner_puertos/escaner_puertos.py 'TARGET'"}}

Sustituye 'TARGET' por la IP o el dominio del servidor objetivo (ej. 127.0.0.1, scanme.nmap.org). Usa ÚNICAMENTE comillas simples (') para envolver los argumentos dentro del comando para evitar romper la estructura del JSON en la terminal.
