"""
WebSocket connection manager.

Keeps track of every connected client and provides helpers to broadcast
structured events (agent_started, agent_progress, agent_completed,
agent_error, pipeline_completed) to all of them.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from models import WSEvent

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages multiple concurrent WebSocket clients."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(self, ws: WebSocket) -> None:
        """Accept and register a new WebSocket client."""
        await ws.accept()
        self._connections.append(ws)
        logger.info("WebSocket client connected  (%d total)", len(self._connections))

    def disconnect(self, ws: WebSocket) -> None:
        """Unregister a WebSocket client."""
        if ws in self._connections:
            self._connections.remove(ws)
        logger.info("WebSocket client disconnected (%d total)", len(self._connections))

    @property
    def active_connections(self) -> int:
        return len(self._connections)

    # ------------------------------------------------------------------
    # Broadcasting
    # ------------------------------------------------------------------

    async def broadcast(self, event: str, data: dict[str, Any] | None = None) -> None:
        """
        Send a JSON event to every connected client.

        Silently drops clients whose connection has closed since the
        last check to avoid crashing the pipeline on a stale socket.
        """
        payload = WSEvent(
            event=event,
            data=data or {},
            timestamp=datetime.utcnow(),
        ).model_dump(mode="json")

        stale: list[WebSocket] = []
        for ws in self._connections:
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_json(payload)
                else:
                    stale.append(ws)
            except Exception:
                logger.warning("Failed to send to WebSocket client; marking stale")
                stale.append(ws)

        for ws in stale:
            self.disconnect(ws)

    # ------------------------------------------------------------------
    # Convenience helpers for each event type
    # ------------------------------------------------------------------

    async def agent_started(self, agent_id: str, agent_name: str) -> None:
        await self.broadcast("agent_started", {
            "agent_id": agent_id,
            "agent_name": agent_name,
        })

    async def agent_progress(self, agent_id: str, message: str, progress: float = 0.0) -> None:
        await self.broadcast("agent_progress", {
            "agent_id": agent_id,
            "message": message,
            "progress": progress,
        })

    async def agent_completed(self, agent_id: str, result: dict[str, Any], duration: float) -> None:
        await self.broadcast("agent_completed", {
            "agent_id": agent_id,
            "result": result,
            "duration": duration,
        })

    async def agent_error(self, agent_id: str, error: str, duration: float) -> None:
        await self.broadcast("agent_error", {
            "agent_id": agent_id,
            "error": error,
            "duration": duration,
        })

    async def pipeline_completed(self, results: dict[str, Any], total_duration: float) -> None:
        await self.broadcast("pipeline_completed", {
            "results": results,
            "total_duration": total_duration,
        })
