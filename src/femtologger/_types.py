"""Core types for FemtoLogger."""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, Protocol, runtime_checkable

LogLevel = Literal["info", "warn", "error"]

LOG_LEVELS: dict[LogLevel, int] = {"info": 0, "warn": 1, "error": 2}


@dataclass(frozen=True, slots=True)
class LogEntry:
    """Immutable log entry passed to transports."""

    level: LogLevel
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, object] | None = None

    def format_metadata_html(self) -> str:
        """Format metadata as HTML-escaped key-value pairs."""
        if not self.metadata:
            return ""
        parts: list[str] = []
        for key, value in self.metadata.items():
            escaped_key = html.escape(str(key), quote=False)
            escaped_value = html.escape(str(value), quote=False)
            parts.append(f"<b>{escaped_key}</b>: {escaped_value}")
        return "\n".join(parts)


@runtime_checkable
class Transport(Protocol):
    """Protocol that all transports must satisfy."""

    async def send(self, entry: LogEntry) -> None: ...
