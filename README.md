# FemtoLogger (Python)

[![PyPI version](https://img.shields.io/pypi/v/femtologger)](https://pypi.org/project/femtologger/)
[![Python versions](https://img.shields.io/pypi/pyversions/femtologger)](https://pypi.org/project/femtologger/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/frederictriquet/FemtoLogger-python/graph/badge.svg)](https://codecov.io/gh/frederictriquet/FemtoLogger-python)

Minimal async logger with Telegram transport for Python.

## Install

```bash
pip install femtologger
```

## Required env vars

```
TELEGRAM_BOT_TOKEN=<bot token from @BotFather>
TELEGRAM_CHAT_ID=<chat id from @userinfobot>
```

## Usage

```python
import asyncio
from femtologger import FemtoLogger, TelegramTransport

logger = FemtoLogger(
    transports=[
        TelegramTransport(
            token="your-bot-token",
            chat_id="your-chat-id",
        ),
    ],
)

async def main():
    await logger.info("User signed up", {"userId": 42})
    await logger.warn("Rate limit approaching", {"current": 95, "max": 100})
    await logger.error("Payment failed", {"orderId": "abc", "reason": "declined"})

asyncio.run(main())
```

## API

### FemtoLogger

```python
FemtoLogger(*, transports: list[Transport], level: LogLevel = "info")
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `transports` | `list[Transport]` | required | List of transport instances |
| `level` | `"info" \| "warn" \| "error"` | `"info"` | Minimum log level |

Methods: `logger.info(message, metadata?)`, `logger.warn(message, metadata?)`, `logger.error(message, metadata?)`. All are async and return `None`.

### TelegramTransport

```python
TelegramTransport(*, token: str, chat_id: str | int, parse_mode: str = "HTML", disable_web_page_preview: bool = True)
```

| Parameter | Type | Default |
|---|---|---|
| `token` | `str` | required |
| `chat_id` | `str \| int` | required |
| `parse_mode` | `str` | `"HTML"` |
| `disable_web_page_preview` | `bool` | `True` |

## Custom transport

Implement the `Transport` protocol:

```python
from femtologger import Transport, LogEntry

class MyTransport:
    async def send(self, entry: LogEntry) -> None:
        # entry.level: "info" | "warn" | "error"
        # entry.message: str
        # entry.metadata: dict[str, object] | None
        # entry.timestamp: datetime
        # IMPORTANT: catch errors internally, never raise
        pass
```

## Key behaviors

- Logger never raises at runtime — transport errors are caught and logged to stderr
- Multiple transports are dispatched in parallel via `asyncio.gather(..., return_exceptions=True)`
- Single runtime dependency (`httpx`), requires Python >= 3.10

## License

MIT
