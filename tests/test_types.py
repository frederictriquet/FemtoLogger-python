"""Tests for _types module."""

from datetime import datetime, timezone

from femtologger._types import LOG_LEVELS, LogEntry, Transport


class TestLogEntry:
    def test_creation(self) -> None:
        entry = LogEntry(level="info", message="hello")
        assert entry.level == "info"
        assert entry.message == "hello"
        assert entry.metadata is None
        assert isinstance(entry.timestamp, datetime)

    def test_creation_with_metadata(self) -> None:
        meta = {"key": "value", "count": 42}
        entry = LogEntry(level="warn", message="test", metadata=meta)
        assert entry.metadata == meta

    def test_frozen(self) -> None:
        entry = LogEntry(level="error", message="oops")
        try:
            entry.level = "info"  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass

    def test_timestamp_is_utc(self) -> None:
        entry = LogEntry(level="info", message="ts")
        assert entry.timestamp.tzinfo == timezone.utc

    def test_format_metadata_html_empty(self) -> None:
        entry = LogEntry(level="info", message="m")
        assert entry.format_metadata_html() == ""

    def test_format_metadata_html(self) -> None:
        entry = LogEntry(level="info", message="m", metadata={"a": 1, "b": "<script>"})
        result = entry.format_metadata_html()
        assert "<b>a</b>: 1" in result
        assert "<b>b</b>: &lt;script&gt;" in result

    def test_custom_timestamp(self) -> None:
        ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
        entry = LogEntry(level="info", message="m", timestamp=ts)
        assert entry.timestamp == ts


class TestLogLevels:
    def test_ordering(self) -> None:
        assert LOG_LEVELS["info"] < LOG_LEVELS["warn"] < LOG_LEVELS["error"]


class TestTransportProtocol:
    def test_protocol_check(self) -> None:
        class GoodTransport:
            async def send(self, entry: LogEntry) -> None:
                pass

        assert isinstance(GoodTransport(), Transport)
