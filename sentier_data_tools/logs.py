import logging
import os
import sys

import structlog


def get_stdout_feedback_logger(name: str, level: int = logging.INFO):
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", "%H:%M:%S%z"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_structlog_stdout_feedback_logger(level: int = logging.INFO):
    structlog.reset_defaults()
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%H:%M:%S%z", utc=False),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logger = structlog.get_logger()
    logger.debug("Starting feedback logger")
    structlog.reset_defaults()
    return logger


if os.getenv("NO_STRUCTLOG"):
    stdout_feedback_logger = get_stdout_feedback_logger("sentier-stdout-feedback")
else:
    stdout_feedback_logger = get_structlog_stdout_feedback_logger()
