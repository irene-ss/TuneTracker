"""
Centralized logging for TuneTracker (guardrails & logging).

One place configures logging; the rest of the app calls the helpers below so that
every query, retrieval, fallback trigger, and error is recorded to logs/app.log
in a consistent format.

Usage:
    from logging_config import setup_logging, log_query, log_retrieval, log_fallback, log_error

    setup_logging()                      # call once at program start
    log_query("calm music for studying")
    log_retrieval(query, results)        # results: list of (title, score) or RetrievalResult
    log_fallback("explainer", "no API key")
    log_error("retriever", exc)          # exc: an Exception
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterable, Optional

# logs/app.log lives at the repo root (this file is in src/, so parent.parent).
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "app.log"

LOGGER_NAME = "tunetracker"
_CONFIGURED = False


def setup_logging(level: int = logging.INFO, echo_to_console: bool = False) -> logging.Logger:
    """
    Configure the shared 'tunetracker' logger to write to logs/app.log.

    Idempotent: safe to call multiple times (handlers are only added once).
    Creates the logs/ directory if it doesn't exist.
    """
    global _CONFIGURED
    logger = logging.getLogger(LOGGER_NAME)

    if _CONFIGURED:
        return logger

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.setLevel(level)
    logger.propagate = False  # don't double-log through the root logger

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if echo_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    _CONFIGURED = True
    logger.info("EVENT=startup | logging initialized -> %s", LOG_FILE)
    return logger


def get_logger() -> logging.Logger:
    """Return the shared logger, configuring it on first use if needed."""
    if not _CONFIGURED:
        return setup_logging()
    return logging.getLogger(LOGGER_NAME)


# --- Event helpers: one function per rubric event type ----------------------

def log_query(query: str, *, k: Optional[int] = None, mode: Optional[str] = None) -> None:
    """Log a user query (free-text search or profile query)."""
    parts = [f"EVENT=query", f'text="{query}"']
    if k is not None:
        parts.append(f"k={k}")
    if mode is not None:
        parts.append(f"mode={mode}")
    get_logger().info(" | ".join(parts))


def log_retrieval(query: str, results: Iterable[Any]) -> None:
    """
    Log a retrieval result set.

    `results` may be RetrievalResult objects (title/score attrs) or (title, score)
    tuples. Logs the count plus a compact title:score summary.
    """
    summary = []
    count = 0
    for item in results:
        count += 1
        title = getattr(item, "title", None)
        score = getattr(item, "score", None)
        if title is None and isinstance(item, (tuple, list)) and len(item) >= 2:
            title, score = item[0], item[1]
        try:
            summary.append(f"{title}:{float(score):.3f}")
        except (TypeError, ValueError):
            summary.append(f"{title}")
    get_logger().info(
        'EVENT=retrieval | query="%s" | hits=%d | results=[%s]',
        query,
        count,
        ", ".join(summary),
    )


def log_fallback(component: str, reason: str) -> None:
    """Log that a fallback path was triggered (e.g. LLM -> template)."""
    get_logger().warning('EVENT=fallback | component=%s | reason="%s"', component, reason)


def log_error(component: str, error: Any) -> None:
    """Log an error. Accepts an Exception or a string; includes a traceback if available."""
    logger = get_logger()
    if isinstance(error, BaseException):
        logger.error(
            'EVENT=error | component=%s | error="%s: %s"',
            component,
            type(error).__name__,
            error,
            exc_info=error,
        )
    else:
        logger.error('EVENT=error | component=%s | error="%s"', component, error)
