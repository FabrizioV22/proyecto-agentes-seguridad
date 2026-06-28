"""
Abstract base class for all security agents.

Provides the common interface (`run`) and a shared helper
(`_run_skill_script`) that launches a skill's Python script as an
asyncio subprocess and returns its parsed JSON output.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from models import PipelineConfig

logger = logging.getLogger(__name__)

# Prefer the project's virtual-env Python; fall back to system python3.
PYTHON_BIN = "/root/proyecto-agentes-seguridad/venv-seguridad/bin/python3"
if not os.path.isfile(PYTHON_BIN):
    PYTHON_BIN = "python3"


class BaseAgent(ABC):
    """
    Every agent must declare its metadata as class-level properties
    and implement the async ``run`` method.
    """

    # -- Metadata (override in subclass) ----------------------------------
    id: str = ""
    name: str = ""
    description: str = ""
    icon: str = "🔍"

    # -- Public API -------------------------------------------------------

    @abstractmethod
    async def run(self, config: PipelineConfig, **kwargs: Any) -> dict[str, Any]:
        """
        Execute the agent's skill and return the parsed result dict.

        Parameters
        ----------
        config : PipelineConfig
            Pipeline-level configuration (targets, enabled agents, …).
        **kwargs :
            Extra keyword arguments.  The orchestrator passes
            ``accumulated_results`` to the GitHub reporter.

        Raises
        ------
        RuntimeError
            If the required target field is missing from *config*.
        """
        ...

    # -- Shared helpers ----------------------------------------------------

    @staticmethod
    async def _run_skill_script(
        script_path: str,
        args: list[str],
        timeout: int = 60,
    ) -> dict[str, Any]:
        """
        Launch *script_path* as an asyncio subprocess and return the
        parsed JSON from its stdout.

        Parameters
        ----------
        script_path : str
            Absolute path to the Python skill script.
        args : list[str]
            Positional arguments forwarded to the script.
        timeout : int
            Maximum seconds before the process is killed.

        Returns
        -------
        dict
            Parsed JSON object.  On failure an ``{"error": …, "status": "error"}``
            dict is returned instead of raising.
        """
        logger.info("Running skill: %s %s (timeout=%ds)", script_path, args, timeout)

        try:
            proc = await asyncio.create_subprocess_exec(
                PYTHON_BIN, script_path, *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )

            stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
            stderr = stderr_bytes.decode("utf-8", errors="replace").strip()

            if proc.returncode != 0 and not stdout:
                return {
                    "error": f"Script exited with code {proc.returncode}: {stderr}",
                    "status": "error",
                }

            # The skill scripts print JSON to stdout.
            if not stdout:
                return {
                    "error": "Script produced no output.",
                    "status": "error",
                }

            try:
                return json.loads(stdout)  # type: ignore[no-any-return]
            except json.JSONDecodeError:
                # Some scripts (crear_issue.py) return plain text instead of JSON.
                return {
                    "raw_output": stdout,
                    "status": "success" if proc.returncode == 0 else "error",
                }

        except asyncio.TimeoutError:
            # Kill the zombie process if it's still alive.
            try:
                proc.kill()  # type: ignore[union-attr]
            except ProcessLookupError:
                pass
            return {
                "error": f"Timeout: script exceeded {timeout}s limit.",
                "status": "error",
            }
        except FileNotFoundError:
            return {
                "error": f"Script not found: {script_path}",
                "status": "error",
            }
        except Exception as exc:
            return {
                "error": str(exc),
                "status": "error",
            }
