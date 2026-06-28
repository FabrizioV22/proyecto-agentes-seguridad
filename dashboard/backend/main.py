"""
FastAPI application — Multi-Agent Security Dashboard Backend.

Exposes REST endpoints for pipeline management and agent inspection,
plus a WebSocket endpoint for real-time progress updates.

Run with:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import logging
import sys
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from models import AgentConfig, AgentResult, AgentStatus, PipelineConfig, PipelineState
from orchestrator import PipelineOrchestrator
from websocket_manager import WebSocketManager

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------
ws_manager = WebSocketManager()
orchestrator = PipelineOrchestrator()


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    logger.info("🚀 Security Dashboard backend starting up")
    yield
    logger.info("🛑 Security Dashboard backend shutting down")
    await orchestrator.stop_pipeline()


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Multi-Agent Security Dashboard API",
    description="Backend for orchestrating security scanning agents.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================================================================
# REST ENDPOINTS
# ===================================================================


# -------------------------------------------------------------------
# Pipeline management
# -------------------------------------------------------------------

@app.post("/api/pipeline/start", summary="Start the security pipeline")
async def pipeline_start(config: PipelineConfig) -> dict[str, Any]:
    """
    Kick off the sequential pipeline with the given configuration.

    Returns immediately — progress is streamed over the WebSocket.
    """
    try:
        await orchestrator.start_pipeline(config, ws_manager)
        return {"message": "Pipeline started", "config": config.model_dump()}
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/pipeline/stop", summary="Stop the running pipeline")
async def pipeline_stop() -> dict[str, str]:
    """Request the running pipeline to stop after the current agent finishes."""
    await orchestrator.stop_pipeline()
    return {"message": "Pipeline stop requested"}


@app.get("/api/pipeline/status", summary="Get pipeline status")
async def pipeline_status() -> dict[str, Any]:
    """Return a snapshot of the current (or last completed) pipeline."""
    status = orchestrator.status
    return {
        "state": status.state.value,
        "current_agent": status.current_agent,
        "completed_agents": status.completed_agents,
        "results": {
            aid: res.model_dump(mode="json") for aid, res in status.results.items()
        },
        "start_time": status.start_time.isoformat() if status.start_time else None,
        "end_time": status.end_time.isoformat() if status.end_time else None,
    }


# -------------------------------------------------------------------
# Agent information
# -------------------------------------------------------------------

@app.get("/api/agents", summary="List all registered agents")
async def list_agents() -> list[dict[str, Any]]:
    """Return metadata about every agent the backend knows about."""
    agents: list[dict[str, Any]] = []
    for agent in orchestrator.agents:
        current_status = AgentStatus.IDLE
        result = orchestrator.get_result(agent.id)
        if result:
            current_status = result.status
        if orchestrator.status.current_agent == agent.id:
            current_status = AgentStatus.RUNNING

        agents.append(
            AgentConfig(
                agent_id=agent.id,
                name=agent.name,
                description=agent.description,
                icon=agent.icon,
                enabled=True,
                status=current_status,
            ).model_dump()
        )
    return agents


@app.post("/api/agents/{agent_id}/run", summary="Run a single agent ad-hoc")
async def run_single_agent(agent_id: str, config: PipelineConfig) -> dict[str, Any]:
    """
    Execute a single agent outside of the pipeline.
    Blocks until the agent completes and returns its result.
    """
    # Prevent running ad-hoc agents while the pipeline is active
    if orchestrator.status.state == PipelineState.RUNNING:
        raise HTTPException(
            status_code=409,
            detail="Cannot run a single agent while the pipeline is running.",
        )

    # Find the agent
    target_agent = None
    for agent in orchestrator.agents:
        if agent.id == agent_id:
            target_agent = agent
            break

    if target_agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")

    # Run it
    await ws_manager.agent_started(agent_id, target_agent.name)
    start = time.monotonic()

    try:
        result = await target_agent.run(config)
        duration = round(time.monotonic() - start, 2)

        status = AgentStatus.ERROR if result.get("status") == "error" else AgentStatus.COMPLETED
        agent_result = AgentResult(
            agent_id=agent_id,
            status=status,
            result=result,
            duration=duration,
            error=result.get("error") if status == AgentStatus.ERROR else None,
        )

        if status == AgentStatus.ERROR:
            await ws_manager.agent_error(agent_id, result.get("error", "Unknown"), duration)
        else:
            await ws_manager.agent_completed(agent_id, result, duration)

        return agent_result.model_dump(mode="json")

    except RuntimeError as exc:
        duration = round(time.monotonic() - start, 2)
        await ws_manager.agent_error(agent_id, str(exc), duration)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        duration = round(time.monotonic() - start, 2)
        error_msg = f"{type(exc).__name__}: {exc}"
        await ws_manager.agent_error(agent_id, error_msg, duration)
        raise HTTPException(status_code=500, detail=error_msg) from exc


# -------------------------------------------------------------------
# Results
# -------------------------------------------------------------------

@app.get("/api/results", summary="Get all collected results")
async def get_results() -> dict[str, Any]:
    """Return every result from the current/last pipeline run."""
    return {
        aid: res.model_dump(mode="json")
        for aid, res in orchestrator.results.items()
    }


@app.get("/api/results/{agent_id}", summary="Get result for a specific agent")
async def get_result(agent_id: str) -> dict[str, Any]:
    """Return the result for a single agent."""
    result = orchestrator.get_result(agent_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No result found for agent '{agent_id}'.",
        )
    return result.model_dump(mode="json")


# ===================================================================
# WEBSOCKET
# ===================================================================

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    """
    Persistent WebSocket connection for real-time pipeline updates.

    Events emitted:
        - agent_started
        - agent_progress
        - agent_completed
        - agent_error
        - pipeline_completed
    """
    await ws_manager.connect(ws)
    try:
        # Keep the connection open; listen for client pings or close.
        while True:
            # We just await incoming messages to keep the connection alive.
            # The client can send JSON commands in the future if needed.
            data = await ws.receive_text()
            logger.debug("WS received from client: %s", data)
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception:
        ws_manager.disconnect(ws)


# ===================================================================
# Health check
# ===================================================================

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
