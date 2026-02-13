"""Telegram transport for FemtoLogger."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from femtologger._types import LogEntry

_LEVEL_EMOJI: dict[str, str] = {
    "info": "\u2139\ufe0f",
    "warn": "\u26a0\ufe0f",
    "error": "\U0001f6a8",
}


class TelegramTransport:
    """Send log entries to a Telegram chat via the Bot API."""

    def __init__(
        self,
        *,
        token: str,
        chat_id: str | int,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True,
    ) -> None:
        if not token:
            raise ValueError("token is required")
        if not chat_id:
            raise ValueError("chat_id is required")
        self._token = token
        self._chat_id = str(chat_id)
        self._parse_mode = parse_mode
        self._disable_web_page_preview = disable_web_page_preview
        self._url = f"https://api.telegram.org/bot{token}/sendMessage"

    def _format(self, entry: LogEntry) -> str:
        emoji = _LEVEL_EMOJI.get(entry.level, "")
        level_upper = entry.level.upper()
        ts = entry.timestamp.isoformat()

        lines = [f"{emoji} <b>[{level_upper}]</b> {entry.message}", f"<i>{ts}</i>"]

        meta_html = entry.format_metadata_html()
        if meta_html:
            lines.append("")
            lines.append(meta_html)

        return "\n".join(lines)

    async def send(self, entry: LogEntry) -> None:
        text = self._format(entry)
        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": self._parse_mode,
            "disable_web_page_preview": self._disable_web_page_preview,
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self._url, json=payload)
                response.raise_for_status()
        except Exception as exc:
            print(f"[femtologger] Telegram error: {exc}", file=sys.stderr)
