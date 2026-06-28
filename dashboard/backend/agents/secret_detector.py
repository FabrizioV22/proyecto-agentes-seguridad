"""
Secret Detector agent — wraps ``detector_secretos/detector_secretos.py``.

Requires ``target_path`` in the pipeline config.
"""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from models import PipelineConfig

SCRIPT_PATH = "/root/proyecto-agentes-seguridad/skills/detector_secretos/detector_secretos.py"
TIMEOUT_SECONDS = 120


class SecretDetectorAgent(BaseAgent):
    id = "secret_detector"
    name = "Detector de Secretos"
    description = "Busca credenciales, API keys y secretos expuestos con Gitleaks."
    icon = "🔑"

    async def run(self, config: PipelineConfig, **kwargs: Any) -> dict[str, Any]:
        if not config.target_path:
            raise RuntimeError("target_path is required for the secret detector agent.")

        return await self._run_skill_script(
            SCRIPT_PATH,
            [config.target_path],
            timeout=TIMEOUT_SECONDS,
        )
