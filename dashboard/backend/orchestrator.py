"""
Pipeline Orchestrator.

Maintains the ordered registry of all 6 security agents, runs them
sequentially according to the pipeline configuration, and emits
WebSocket events at every stage.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime
from typing import Any

from agents import (
    CodeScannerAgent,
    DepAuditorAgent,
    GitHubReporterAgent,
    PortScannerAgent,
    SecretDetectorAgent,
    WebAuditorAgent,
)
from agents.base_agent import BaseAgent
from models import AgentResult, AgentStatus, PipelineConfig, PipelineState, PipelineStatus
from websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """
    Runs enabled agents one-by-one, collects their results, and feeds the
    accumulated data to the final GitHub Reporter agent.
    """

    # Canonical agent order — the pipeline always follows this sequence.
    ALL_AGENTS: list[BaseAgent] = [
        PortScannerAgent(),
        WebAuditorAgent(),
        CodeScannerAgent(),
        SecretDetectorAgent(),
        DepAuditorAgent(),
        GitHubReporterAgent(),
    ]

    def __init__(self) -> None:
        self._status = PipelineStatus()
        self._current_task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def status(self) -> PipelineStatus:
        return self._status

    @property
    def agents(self) -> list[BaseAgent]:
        return self.ALL_AGENTS

    @property
    def results(self) -> dict[str, AgentResult]:
        return self._status.results

    def get_result(self, agent_id: str) -> AgentResult | None:
        return self._status.results.get(agent_id)

    # ------------------------------------------------------------------
    # Pipeline lifecycle
    # ------------------------------------------------------------------

    async def start_pipeline(
        self,
        config: PipelineConfig,
        ws_manager: WebSocketManager,
    ) -> None:
        """
        Launch the sequential pipeline in a background task.

        Raises ``RuntimeError`` if a pipeline is already running.
        """
        if self._status.state == PipelineState.RUNNING:
            raise RuntimeError("A pipeline is already running.")

        self._stop_event.clear()
        self._status = PipelineStatus(
            state=PipelineState.RUNNING,
            start_time=datetime.utcnow(),
        )

        self._current_task = asyncio.create_task(
            self._run_pipeline(config, ws_manager),
            name="pipeline-run",
        )

    async def stop_pipeline(self) -> None:
        """Signal the running pipeline to stop after the current agent finishes."""
        if self._status.state != PipelineState.RUNNING:
            return
        self._status.state = PipelineState.STOPPING
        self._stop_event.set()

    # ------------------------------------------------------------------
    # Internal pipeline loop
    # ------------------------------------------------------------------

    async def _run_pipeline(
        self,
        config: PipelineConfig,
        ws_manager: WebSocketManager,
    ) -> None:
        pipeline_start = time.monotonic()
        accumulated_results: dict[str, dict[str, Any]] = {}

        try:
            for agent in self.ALL_AGENTS:
                # Respect stop signal
                if self._stop_event.is_set():
                    logger.info("Pipeline stop requested — aborting before %s", agent.id)
                    break

                # Skip agents not in the enabled list
                if agent.id not in config.enabled_agents:
                    logger.info("Agent %s is disabled — skipping", agent.id)
                    self._record_result(agent.id, AgentStatus.SKIPPED, {}, 0.0)
                    continue

                # Check if the agent has the required target
                if not self._has_required_target(agent, config):
                    logger.info("Agent %s lacks required target — skipping", agent.id)
                    skip_result = AgentResult(
                        agent_id=agent.id,
                        status=AgentStatus.SKIPPED,
                        result={"message": "Target not configured; agent skipped."},
                        duration=0.0,
                    )
                    self._status.results[agent.id] = skip_result
                    self._status.completed_agents.append(agent.id)
                    await ws_manager.agent_completed(agent.id, skip_result.result, 0.0)
                    continue

                # -- Execute the agent --
                self._status.current_agent = agent.id
                await ws_manager.agent_started(agent.id, agent.name)
                await ws_manager.agent_progress(agent.id, "Ejecutando…", 0.0)

                agent_start = time.monotonic()
                try:
                    kwargs: dict[str, Any] = {}
                    if agent.id == "github_reporter":
                        kwargs["accumulated_results"] = accumulated_results

                    result = await agent.run(config, **kwargs)
                    duration = round(time.monotonic() - agent_start, 2)

                    status = AgentStatus.ERROR if result.get("status") == "error" else AgentStatus.COMPLETED
                    self._record_result(agent.id, status, result, duration)
                    accumulated_results[agent.id] = result

                    if status == AgentStatus.ERROR:
                        await ws_manager.agent_error(
                            agent.id,
                            result.get("error", "Unknown error"),
                            duration,
                        )
                    else:
                        await ws_manager.agent_completed(agent.id, result, duration)

                except RuntimeError as exc:
                    # Missing required target — skip gracefully
                    duration = round(time.monotonic() - agent_start, 2)
                    self._record_result(
                        agent.id, AgentStatus.SKIPPED,
                        {"message": str(exc)}, duration,
                    )
                    await ws_manager.agent_completed(
                        agent.id, {"message": str(exc), "status": "skipped"}, duration,
                    )

                except Exception as exc:
                    duration = round(time.monotonic() - agent_start, 2)
                    logger.exception("Agent %s crashed", agent.id)
                    error_msg = f"{type(exc).__name__}: {exc}"
                    self._record_result(
                        agent.id, AgentStatus.ERROR,
                        {"error": error_msg}, duration, error_msg,
                    )
                    await ws_manager.agent_error(agent.id, error_msg, duration)

            # -- Pipeline finished --
            total_duration = round(time.monotonic() - pipeline_start, 2)
            self._status.state = PipelineState.COMPLETED
            self._status.current_agent = None
            self._status.end_time = datetime.utcnow()

            serialised_results = {
                aid: res.model_dump(mode="json")
                for aid, res in self._status.results.items()
            }
            await ws_manager.pipeline_completed(serialised_results, total_duration)

        except Exception as exc:
            logger.exception("Pipeline crashed unexpectedly")
            self._status.state = PipelineState.ERROR
            self._status.current_agent = None
            self._status.end_time = datetime.utcnow()
            await ws_manager.broadcast("pipeline_error", {"error": str(exc)})

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _record_result(
        self,
        agent_id: str,
        status: AgentStatus,
        result: dict[str, Any],
        duration: float,
        error: str | None = None,
    ) -> None:
        self._status.results[agent_id] = AgentResult(
            agent_id=agent_id,
            status=status,
            result=result,
            duration=duration,
            error=error,
        )
        if agent_id not in self._status.completed_agents:
            self._status.completed_agents.append(agent_id)

    @staticmethod
    def _has_required_target(agent: BaseAgent, config: PipelineConfig) -> bool:
        """Return whether *config* supplies the target that *agent* needs."""
        needs_ip = {"port_scanner"}
        needs_url = {"web_auditor"}
        needs_path = {"code_scanner", "secret_detector", "dep_auditor"}

        if agent.id in needs_ip and not config.target_ip:
            return False
        if agent.id in needs_url and not config.target_url:
            return False
        if agent.id in needs_path and not config.target_path:
            return False
        # github_reporter has no external target requirement
        return True
