"""FemtoLogger — minimal async logger with pluggable transports."""

from __future__ import annotations

import asyncio
import sys
from femtologger._types import LOG_LEVELS, LogEntry, LogLevel, Transport


class FemtoLogger:
    """Async logger that dispatches log entries to multiple transports."""

    def __init__(
        self,
        *,
        transports: list[Transport],
        level: LogLevel = "info",
    ) -> None:
        if not transports:
            raise ValueError("At least one transport is required")
        if level not in LOG_LEVELS:
            raise ValueError(f"Invalid log level: {level!r}")
        self._transports = list(transports)
        self._level: LogLevel = level

    def _should_log(self, level: LogLevel) -> bool:
        return LOG_LEVELS[level] >= LOG_LEVELS[self._level]

    async def _dispatch(self, entry: LogEntry) -> None:
        results = await asyncio.gather(
            *(t.send(entry) for t in self._transports),
            return_exceptions=True,
        )
        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                print(
                    f"[femtologger] transport {i} error: {result}",
                    file=sys.stderr,
                )

    async def info(
        self, message: str, metadata: dict[str, object] | None = None
    ) -> None:
        if self._should_log("info"):
            await self._dispatch(LogEntry(level="info", message=message, metadata=metadata))

    async def warn(
        self, message: str, metadata: dict[str, object] | None = None
    ) -> None:
        if self._should_log("warn"):
            await self._dispatch(LogEntry(level="warn", message=message, metadata=metadata))

    async def error(
        self, message: str, metadata: dict[str, object] | None = None
    ) -> None:
        if self._should_log("error"):
            await self._dispatch(LogEntry(level="error", message=message, metadata=metadata))
