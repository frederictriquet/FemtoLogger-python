# FemtoLogger Python — Dev Guide

## Commands

```bash
uv sync                                          # Install deps
uv run pytest --cov=femtologger --cov-report=term # Tests + coverage
uv run pyright                                    # Type check (strict)
uv build                                          # Build wheel + sdist
```

## Architecture

- `src/femtologger/_types.py` — Core types: `LogLevel`, `LogEntry`, `Transport` Protocol
- `src/femtologger/_logger.py` — `FemtoLogger` class (dispatch, level filtering)
- `src/femtologger/transports/_telegram.py` — `TelegramTransport` (httpx, HTML formatting)
- Tests mirror source structure in `tests/`

## Key design decisions

- **Async-only** — matches the TypeScript version; use `asyncio.run()` for sync contexts
- **Transport Protocol** — structural typing via `typing.Protocol`, no base class needed
- **Error isolation** — `asyncio.gather(..., return_exceptions=True)`, errors go to stderr
- **Single runtime dep** — `httpx` only; dev deps: pyright, pytest, pytest-asyncio, respx, pytest-cov
- **HTML escaping** — metadata values only (not the message itself), matching TS behavior
