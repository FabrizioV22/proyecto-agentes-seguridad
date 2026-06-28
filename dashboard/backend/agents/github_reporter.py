"""
GitHub Reporter agent — wraps ``github_issues/crear_issue.py``.

Unlike the other agents this one does NOT require a target field.
Instead it consumes ``accumulated_results`` (passed by the orchestrator)
to build a consolidated Markdown security report and creates a GitHub
issue via the ``gh`` CLI.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from agents.base_agent import BaseAgent
from models import PipelineConfig

SCRIPT_PATH = "/root/proyecto-agentes-seguridad/skills/github_issues/crear_issue.py"
TIMEOUT_SECONDS = 30


class GitHubReporterAgent(BaseAgent):
    id = "github_reporter"
    name = "Reportero GitHub"
    description = "Consolida los hallazgos de todos los agentes y crea un issue en GitHub."
    icon = "📋"

    async def run(self, config: PipelineConfig, **kwargs: Any) -> dict[str, Any]:
        accumulated_results: dict[str, dict[str, Any]] = kwargs.get("accumulated_results", {})

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        title = f"Reporte de Auditoría de Seguridad - {timestamp}"
        body = self._build_report_body(accumulated_results, config)

        return await self._run_skill_script(
            SCRIPT_PATH,
            [title, body],
            timeout=TIMEOUT_SECONDS,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_report_body(
        results: dict[str, dict[str, Any]],
        config: PipelineConfig,
    ) -> str:
        """Build a Markdown body summarising every agent's findings."""

        lines: list[str] = [
            "# 🛡️ Reporte de Auditoría de Seguridad",
            "",
            "## Configuración del Escaneo",
            "",
        ]

        if config.target_ip:
            lines.append(f"- **IP/Dominio objetivo:** `{config.target_ip}`")
        if config.target_url:
            lines.append(f"- **URL objetivo:** `{config.target_url}`")
        if config.target_path:
            lines.append(f"- **Ruta objetivo:** `{config.target_path}`")

        lines += ["", "---", ""]

        # Map agent IDs to friendly section headers
        section_titles: dict[str, str] = {
            "port_scanner": "🔌 Escaneo de Puertos (Nmap)",
            "web_auditor": "🌐 Auditoría Web (SQLMap)",
            "code_scanner": "📝 Escaneo de Código (Bandit)",
            "secret_detector": "🔑 Detección de Secretos (Gitleaks)",
            "dep_auditor": "📦 Auditoría de Dependencias (Safety)",
        }

        if not results:
            lines.append("_No se obtuvieron resultados de ningún agente._")
        else:
            for agent_id, section_title in section_titles.items():
                result = results.get(agent_id)
                if result is None:
                    continue

                lines.append(f"## {section_title}")
                lines.append("")

                status = result.get("status", "unknown")
                if status == "error":
                    error_msg = result.get("error", "Error desconocido")
                    lines.append(f"⚠️ **Error:** {error_msg}")
                elif status == "skipped":
                    lines.append("_Agente omitido (configuración de objetivo faltante)._")
                else:
                    # Dump relevant keys; exclude meta fields
                    for key, value in result.items():
                        if key in {"status", "raw_output"}:
                            continue
                        if isinstance(value, list):
                            lines.append(f"**{key}:** {len(value)} elemento(s)")
                            for item in value[:20]:  # cap to avoid enormous bodies
                                lines.append(f"  - `{item}`" if isinstance(item, str) else f"  - {item}")
                        elif isinstance(value, dict):
                            lines.append(f"**{key}:**")
                            for k, v in value.items():
                                lines.append(f"  - {k}: `{v}`")
                        else:
                            lines.append(f"**{key}:** {value}")

                lines += ["", "---", ""]

        lines += [
            "",
            f"_Generado automáticamente por el Dashboard de Seguridad Multi-Agente — "
            f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}_",
        ]

        return "\n".join(lines)
