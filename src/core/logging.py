# src/core/logging.py — Structured JSON Logging

"""Logging estruturado em JSON para observabilidade.
Substitui print() e st.warning/error por logs consistentes.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formatter que produz JSON estruturado."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Adiciona campos extras se existirem
        if hasattr(record, "extra_fields") and record.extra_fields:
            log_obj.update(record.extra_fields)

        # Exception info
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False)


def setup_logging(level: str = "INFO", json_format: bool = True) -> None:
    """Configura logging global.
    
    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        json_format: Se True, usa JSON; se False, usa formato humano

    """
    handler = logging.StreamHandler(sys.stdout)

    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S"
        ))

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    # Reduz verbosidade de libs terceiras
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("streamlit").setLevel(logging.WARNING)
    logging.getLogger("folium").setLevel(logging.WARNING)
    logging.getLogger("pyproj").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Retorna logger configurado para o módulo."""
    return logging.getLogger(name)


# Convenience functions para uso direto
def log_info(logger: logging.Logger, message: str, **extra: Any) -> None:
    """Log INFO com campos extras."""
    logger.info(message, extra={"extra_fields": extra} if extra else None)


def log_warning(logger: logging.Logger, message: str, **extra: Any) -> None:
    """Log WARNING com campos extras."""
    logger.warning(message, extra={"extra_fields": extra} if extra else None)


def log_error(logger: logging.Logger, message: str, **extra: Any) -> None:
    """Log ERROR com campos extras."""
    logger.error(message, extra={"extra_fields": extra} if extra else None)


def log_exception(logger: logging.Logger, message: str, **extra: Any) -> None:
    """Log EXCEPTION com traceback e campos extras."""
    logger.exception(message, extra={"extra_fields": extra} if extra else None)
