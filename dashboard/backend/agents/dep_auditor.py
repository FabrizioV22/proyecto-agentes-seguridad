"""
Dependency Auditor agent — wraps ``auditor_dependencias/auditor_dependencias.py``.

Requires ``target_path`` in the pipeline config.
"""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from models import PipelineConfig

SCRIPT_PATH = "/root/proyecto-agentes-seguridad/skills/auditor_dependencias/auditor_dependencias.py"
TIMEOUT_SECONDS = 60


class DepAuditorAgent(BaseAgent):
    id = "dep_auditor"
    name = "Auditor de Dependencias"
    description = "Verifica vulnerabilidades conocidas en las dependencias del proyecto (Safety)."
    icon = "📦"

    async def run(self, config: PipelineConfig, **kwargs: Any) -> dict[str, Any]:
        if not config.target_path:
            raise RuntimeError("target_path is required for the dependency auditor agent.")

        return await self._run_skill_script(
            SCRIPT_PATH,
            [config.target_path],
            timeout=TIMEOUT_SECONDS,
        )
