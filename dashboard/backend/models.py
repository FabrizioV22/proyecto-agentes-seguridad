"""
Pydantic models for the multi-agent security dashboard.

Defines the data contracts for agent configuration, pipeline management,
and result reporting used across the REST API and WebSocket events.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AgentStatus(str, Enum):
    """Possible lifecycle states for an individual agent."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    SKIPPED = "skipped"


class PipelineState(str, Enum):
    """Top-level state of the pipeline."""
    IDLE = "idle"
    RUNNING = "running"
    STOPPING = "stopping"
    COMPLETED = "completed"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Agent models
# ---------------------------------------------------------------------------

class AgentConfig(BaseModel):
    """Describes a registered agent and its current state."""
    agent_id: str = Field(..., description="Unique identifier, e.g. 'port_scanner'")
    name: str = Field(..., description="Human-readable name")
    description: str = Field("", description="What the agent does")
    icon: str = Field("🔍", description="Emoji icon for the UI")
    enabled: bool = Field(True, description="Whether the agent is enabled in the current pipeline")
    status: AgentStatus = Field(AgentStatus.IDLE, description="Current runtime status")


# ---------------------------------------------------------------------------
# Pipeline models
# ---------------------------------------------------------------------------

class PipelineConfig(BaseModel):
    """
    Input configuration sent by the frontend to start a pipeline run.
    All target fields are optional — agents will be skipped when their
    required target is missing.
    """
    target_ip: Optional[str] = Field(None, description="IP or domain for the port scanner")
    target_url: Optional[str] = Field(None, description="URL for the web auditor (sqlmap)")
    target_path: Optional[str] = Field(None, description="File/dir path for code scanner, secret detector, and dep auditor")
    enabled_agents: list[str] = Field(
        default_factory=lambda: [
            "port_scanner",
            "web_auditor",
            "code_scanner",
            "secret_detector",
            "dep_auditor",
            "github_reporter",
        ],
        description="Ordered list of agent IDs to execute",
    )


class PipelineStatus(BaseModel):
    """Snapshot of the currently running (or last completed) pipeline."""
    state: PipelineState = Field(PipelineState.IDLE)
    current_agent: Optional[str] = Field(None, description="Agent ID currently executing")
    completed_agents: list[str] = Field(default_factory=list)
    results: dict[str, AgentResult] = Field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------

class AgentResult(BaseModel):
    """Outcome of a single agent execution."""
    agent_id: str
    status: AgentStatus
    result: dict[str, Any] = Field(default_factory=dict, description="Parsed JSON output from the skill script")
    duration: float = Field(0.0, description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# WebSocket event models
# ---------------------------------------------------------------------------

class WSEvent(BaseModel):
    """Envelope sent over the WebSocket connection."""
    event: str = Field(..., description="Event type, e.g. 'agent_started'")
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Rebuild PipelineStatus so the forward-ref to AgentResult resolves
PipelineStatus.model_rebuild()
