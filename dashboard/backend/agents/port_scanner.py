"""
Port Scanner agent — wraps ``escaner_puertos/escaner_puertos.py``.

Requires ``target_ip`` in the pipeline config.
"""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from models import PipelineConfig

SCRIPT_PATH = "/root/proyecto-agentes-seguridad/skills/escaner_puertos/escaner_puertos.py"
TIMEOUT_SECONDS = 90


class PortScannerAgent(BaseAgent):
    id = "port_scanner"
    name = "Escáner de Puertos"
    description = "Escanea los puertos abiertos y servicios de un objetivo usando Nmap."
    icon = "🔌"

    async def run(self, config: PipelineConfig, **kwargs: Any) -> dict[str, Any]:
        if not config.target_ip:
            raise RuntimeError("target_ip is required for the port scanner agent.")

        return await self._run_skill_script(
            SCRIPT_PATH,
            [config.target_ip],
            timeout=TIMEOUT_SECONDS,
        )
