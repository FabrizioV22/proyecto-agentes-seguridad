"""
Code Scanner agent — wraps ``escaner_codigo/escaner_codigo.py``.

Requires ``target_path`` in the pipeline config.
"""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from models import PipelineConfig

SCRIPT_PATH = "/root/proyecto-agentes-seguridad/skills/escaner_codigo/escaner_codigo.py"
TIMEOUT_SECONDS = 60


class CodeScannerAgent(BaseAgent):
    id = "code_scanner"
    name = "Escáner de Código"
    description = "Analiza código fuente en busca de vulnerabilidades usando Bandit."
    icon = "📝"

    async def run(self, config: PipelineConfig, **kwargs: Any) -> dict[str, Any]:
        if not config.target_path:
            raise RuntimeError("target_path is required for the code scanner agent.")

        return await self._run_skill_script(
            SCRIPT_PATH,
            [config.target_path],
            timeout=TIMEOUT_SECONDS,
        )
