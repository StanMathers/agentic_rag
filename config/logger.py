import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
_RESERVED_ATTRS = set(vars(logging.makeLogRecord({}))) | {
    "message",
    "asctime",
    "taskName",
}


def set_request_id(request_id: str | None = None) -> str:
    """Set the request id for the current context. Generates a UUID if none is given."""
    request_id = request_id or str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


def get_request_id() -> str | None:
    return request_id_var.get()


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # An explicit extra={"request_id": ...} takes precedence over the context value.
        if getattr(record, "request_id", None) is None:
            record.request_id = request_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    @staticmethod
    def _caller(record: logging.LogRecord) -> str:
        # Module-level calls have funcName "<module>"; use the module name instead.
        return record.module if record.funcName == "<module>" else record.funcName

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "message": f"[{self._caller(record)}]: {record.getMessage()}",
            "request_id": getattr(record, "request_id", None),
        }
        for key, value in vars(record).items():
            if key not in _RESERVED_ATTRS and key not in log:
                log[key] = value
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log, default=str)


def get_logger(name: str = "agentic_rag", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        handler.addFilter(RequestIdFilter())
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger


logger = get_logger()
