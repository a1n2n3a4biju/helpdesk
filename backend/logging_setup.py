"""Application logging.

- Logs go to the console and (if LOG_FILE is set) to a rotating file.
- Every record passes through RedactSecretsFilter, so a password or key that slips
  into a message is masked before it is written anywhere.
- Code logs IDs and enum values (status, priority, category) only, never ticket
  titles, descriptions, comments or requester emails.
"""
import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import Request

from services.safety import redact_secrets

LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s | %(message)s"


class RedactSecretsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        clean = redact_secrets(message)
        if clean != message:
            record.msg, record.args = clean, None
        return True


def setup_logging(level: str = "INFO", log_file: str | None = None) -> None:
    root = logging.getLogger("helpdesk")
    if getattr(root, "_configured", False):
        return
    root.setLevel(level.upper())
    root.propagate = True  # lets pytest's caplog see records
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"))
    for handler in handlers:
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        handler.addFilter(RedactSecretsFilter())
        root.addHandler(handler)
    root._configured = True


request_log = logging.getLogger("helpdesk.http")


async def log_requests(request: Request, call_next):
    """One line per request: method, path, status and duration. No bodies or query values."""
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        request_log.exception("%s %s -> unhandled error", request.method, request.url.path)
        raise
    duration = (time.perf_counter() - started) * 1000
    level = logging.WARNING if response.status_code >= 500 else logging.INFO
    request_log.log(level, "%s %s -> %s (%d ms)", request.method, request.url.path,
                    response.status_code, duration)
    return response
