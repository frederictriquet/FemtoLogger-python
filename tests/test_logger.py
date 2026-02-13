"""Tests for FemtoLogger."""

import pytest

from femtologger._logger import FemtoLogger
from femtologger._types import LogEntry


class FakeTransport:
    """In-memory transport for testing."""

    def __init__(self) -> None:
        self.entries: list[LogEntry] = []

    async def send(self, entry: LogEntry) -> None:
        self.entries.append(entry)


class FailingTransport:
    """Transport that always raises."""

    async def send(self, entry: LogEntry) -> None:
        raise RuntimeError("boom")


class TestFemtoLoggerInit:
    def test_requires_transports(self) -> None:
        with pytest.raises(ValueError, match="At least one transport"):
            FemtoLogger(transports=[])

    def test_rejects_invalid_level(self) -> None:
        t = FakeTransport()
        with pytest.raises(ValueError, match="Invalid log level"):
            FemtoLogger(transports=[t], level="debug")  # type: ignore[arg-type]


class TestFemtoLoggerDispatch:
    async def test_info(self) -> None:
        t = FakeTransport()
        logger = FemtoLogger(transports=[t])
        await logger.info("hello")
        assert len(t.entries) == 1
        assert t.entries[0].level == "info"
        assert t.entries[0].message == "hello"

    async def test_warn(self) -> None:
        t = FakeTransport()
        logger = FemtoLogger(transports=[t])
        await logger.warn("warning")
        assert len(t.entries) == 1
        assert t.entries[0].level == "warn"

    async def test_error(self) -> None:
        t = FakeTransport()
        logger = FemtoLogger(transports=[t])
        await logger.error("fail")
        assert len(t.entries) == 1
        assert t.entries[0].level == "error"

    async def test_metadata_passed(self) -> None:
        t = FakeTransport()
        logger = FemtoLogger(transports=[t])
        await logger.info("hi", {"key": "val"})
        assert t.entries[0].metadata == {"key": "val"}

    async def test_multiple_transports(self) -> None:
        t1 = FakeTransport()
        t2 = FakeTransport()
        logger = FemtoLogger(transports=[t1, t2])
        await logger.info("msg")
        assert len(t1.entries) == 1
        assert len(t2.entries) == 1


class TestLevelFiltering:
    async def test_warn_level_filters_info(self) -> None:
        t = FakeTransport()
        logger = FemtoLogger(transports=[t], level="warn")
        await logger.info("should not appear")
        await logger.warn("should appear")
        await logger.error("should also appear")
        assert len(t.entries) == 2
        assert t.entries[0].level == "warn"
        assert t.entries[1].level == "error"

    async def test_error_level_filters_info_and_warn(self) -> None:
        t = FakeTransport()
        logger = FemtoLogger(transports=[t], level="error")
        await logger.info("no")
        await logger.warn("no")
        await logger.error("yes")
        assert len(t.entries) == 1
        assert t.entries[0].level == "error"

    async def test_info_level_passes_all(self) -> None:
        t = FakeTransport()
        logger = FemtoLogger(transports=[t], level="info")
        await logger.info("a")
        await logger.warn("b")
        await logger.error("c")
        assert len(t.entries) == 3


class TestErrorHandling:
    async def test_failing_transport_does_not_raise(self) -> None:
        logger = FemtoLogger(transports=[FailingTransport()])
        await logger.info("should not raise")

    async def test_failing_transport_does_not_block_others(self) -> None:
        t = FakeTransport()
        logger = FemtoLogger(transports=[FailingTransport(), t])
        await logger.info("msg")
        assert len(t.entries) == 1

    async def test_error_logged_to_stderr(self, capsys: pytest.CaptureFixture[str]) -> None:
        logger = FemtoLogger(transports=[FailingTransport()])
        await logger.info("msg")
        captured = capsys.readouterr()
        assert "transport 0 error" in captured.err
        assert "boom" in captured.err
