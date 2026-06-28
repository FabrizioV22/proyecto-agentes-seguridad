"""
agents — Thin wrappers around the project's standalone security skill scripts.

Each agent inherits from BaseAgent and implements `run()` to invoke its
corresponding CLI tool via asyncio subprocess.
"""

from agents.port_scanner import PortScannerAgent
from agents.web_auditor import WebAuditorAgent
from agents.code_scanner import CodeScannerAgent
from agents.secret_detector import SecretDetectorAgent
from agents.dep_auditor import DepAuditorAgent
from agents.github_reporter import GitHubReporterAgent

__all__ = [
    "PortScannerAgent",
    "WebAuditorAgent",
    "CodeScannerAgent",
    "SecretDetectorAgent",
    "DepAuditorAgent",
    "GitHubReporterAgent",
]
