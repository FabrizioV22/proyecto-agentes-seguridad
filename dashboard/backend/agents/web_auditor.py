"""
Web Auditor agent — wraps ``auditor_web/sqlmap_runner.py``.

Requires ``target_url`` in the pipeline config.
"""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from models import PipelineConfig

SCRIPT_PATH = "/root/proyecto-agentes-seguridad/skills/auditor_web/sqlmap_runner.py"
TIMEOUT_SECONDS = 300


class WebAuditorAgent(BaseAgent):
    id = "web_auditor"
    name = "Auditor Web (SQLMap)"
    description = "Detecta vulnerabilidades de inyección SQL en una URL objetivo."
    icon = "🌐"

    async def run(self, config: PipelineConfig, **kwargs: Any) -> dict[str, Any]:
        if not config.target_url:
            raise RuntimeError("target_url is required for the web auditor agent.")

        return await self._run_skill_script(
            SCRIPT_PATH,
            [config.target_url],
            timeout=TIMEOUT_SECONDS,
        )
