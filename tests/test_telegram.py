"""Tests for TelegramTransport."""

from datetime import datetime, timezone

import httpx
import pytest
import respx

from femtologger._types import LogEntry
from femtologger.transports._telegram import TelegramTransport


@pytest.fixture
def transport() -> TelegramTransport:
    return TelegramTransport(token="fake-token", chat_id="12345")


class TestTelegramInit:
    def test_requires_token(self) -> None:
        with pytest.raises(ValueError, match="token"):
            TelegramTransport(token="", chat_id="123")

    def test_requires_chat_id(self) -> None:
        with pytest.raises(ValueError, match="chat_id"):
            TelegramTransport(token="tok", chat_id="")

    def test_default_options(self, transport: TelegramTransport) -> None:
        assert transport._parse_mode == "HTML"
        assert transport._disable_web_page_preview is True

    def test_custom_options(self) -> None:
        t = TelegramTransport(
            token="tok",
            chat_id=999,
            parse_mode="MarkdownV2",
            disable_web_page_preview=False,
        )
        assert t._parse_mode == "MarkdownV2"
        assert t._disable_web_page_preview is False
        assert t._chat_id == "999"


class TestTelegramFormat:
    def test_info_format(self, transport: TelegramTransport) -> None:
        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        entry = LogEntry(level="info", message="test msg", timestamp=ts)
        result = transport._format(entry)
        assert "[INFO]" in result
        assert "test msg" in result
        assert "2024-06-15" in result

    def test_warn_format(self, transport: TelegramTransport) -> None:
        entry = LogEntry(level="warn", message="watch out")
        result = transport._format(entry)
        assert "[WARN]" in result

    def test_error_format(self, transport: TelegramTransport) -> None:
        entry = LogEntry(level="error", message="oh no")
        result = transport._format(entry)
        assert "[ERROR]" in result

    def test_metadata_in_format(self, transport: TelegramTransport) -> None:
        entry = LogEntry(level="info", message="m", metadata={"userId": 42})
        result = transport._format(entry)
        assert "userId" in result
        assert "42" in result

    def test_html_escape_in_metadata(self, transport: TelegramTransport) -> None:
        entry = LogEntry(level="info", message="m", metadata={"x": "<b>bad</b>"})
        result = transport._format(entry)
        assert "&lt;b&gt;bad&lt;/b&gt;" in result


class TestTelegramSend:
    @respx.mock
    async def test_successful_send(self, transport: TelegramTransport) -> None:
        route = respx.post("https://api.telegram.org/botfake-token/sendMessage").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        entry = LogEntry(level="info", message="hello")
        await transport.send(entry)
        assert route.called
        request = route.calls[0].request
        body = request.content.decode()
        assert "12345" in body
        assert "hello" in body

    @respx.mock
    async def test_api_error_does_not_raise(
        self, transport: TelegramTransport, capsys: pytest.CaptureFixture[str]
    ) -> None:
        respx.post("https://api.telegram.org/botfake-token/sendMessage").mock(
            return_value=httpx.Response(500, json={"ok": False})
        )
        entry = LogEntry(level="error", message="test")
        await transport.send(entry)
        captured = capsys.readouterr()
        assert "Telegram error" in captured.err

    @respx.mock
    async def test_network_error_does_not_raise(
        self, transport: TelegramTransport, capsys: pytest.CaptureFixture[str]
    ) -> None:
        respx.post("https://api.telegram.org/botfake-token/sendMessage").mock(
            side_effect=httpx.ConnectError("offline")
        )
        entry = LogEntry(level="info", message="test")
        await transport.send(entry)
        captured = capsys.readouterr()
        assert "Telegram error" in captured.err
