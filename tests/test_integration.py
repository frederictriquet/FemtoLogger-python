"""Integration tests — full logger with mocked Telegram API."""

import httpx
import respx

from femtologger import FemtoLogger, TelegramTransport
from femtologger._types import LogEntry


class FakeTransport:
    def __init__(self) -> None:
        self.entries: list[LogEntry] = []

    async def send(self, entry: LogEntry) -> None:
        self.entries.append(entry)


class TestIntegration:
    @respx.mock
    async def test_full_flow(self) -> None:
        route = respx.post("https://api.telegram.org/bottok123/sendMessage").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        telegram = TelegramTransport(token="tok123", chat_id="999")
        fake = FakeTransport()
        logger = FemtoLogger(transports=[telegram, fake])

        await logger.info("User signed up", {"userId": 42})
        await logger.warn("Rate limit", {"current": 95})
        await logger.error("Payment failed", {"orderId": "abc"})

        assert route.call_count == 3
        assert len(fake.entries) == 3
        assert fake.entries[0].level == "info"
        assert fake.entries[1].level == "warn"
        assert fake.entries[2].level == "error"

    @respx.mock
    async def test_level_filtering_with_telegram(self) -> None:
        route = respx.post("https://api.telegram.org/bottok123/sendMessage").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        telegram = TelegramTransport(token="tok123", chat_id="999")
        logger = FemtoLogger(transports=[telegram], level="error")

        await logger.info("skip")
        await logger.warn("skip")
        await logger.error("keep")

        assert route.call_count == 1

    @respx.mock
    async def test_telegram_failure_does_not_block_other_transports(self) -> None:
        respx.post("https://api.telegram.org/bottok123/sendMessage").mock(
            return_value=httpx.Response(500, json={"ok": False})
        )
        telegram = TelegramTransport(token="tok123", chat_id="999")
        fake = FakeTransport()
        logger = FemtoLogger(transports=[telegram, fake])

        await logger.info("msg")
        assert len(fake.entries) == 1
