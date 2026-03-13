# CLAUDE.md

## Structured Logging Setup (Django + structlog)

When adding structured logging to a Django project, follow these steps exactly:

### 1. Add dependencies

Add these to `pyproject.toml` (or install via pip/uv):

```
django-structlog>=8.0.0
rich>=13.0.0
structlog>=25.5.0
```

### 2. Register the app and middleware

In `settings.py`:

- Add `"django_structlog"` to `INSTALLED_APPS` (in the third-party section).
- Add `"django_structlog.middlewares.RequestMiddleware"` to `MIDDLEWARE`, immediately after `SecurityMiddleware`.

### 3. Configure structlog and Django LOGGING

Add the following block to the bottom of `settings.py`:

```python
import structlog  # place with other imports at top of file

_common_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.UnicodeDecoder(),
]

_renderer = (
    structlog.dev.ConsoleRenderer()
    if DEBUG
    else structlog.processors.JSONRenderer()
)

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        *_common_processors,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processors": [
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                _renderer,
            ],
            "foreign_pre_chain": _common_processors,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structured",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG" if DEBUG else "INFO",
    },
    "loggers": {
        "django": {
            "level": "INFO",
        },
        "django.server": {
            "level": "WARNING",
        },
        "django_structlog": {
            "level": "INFO",
        },
    },
}
```

### 4. Key design decisions

- **DEBUG mode** uses `ConsoleRenderer()` for colored, human-readable output. **Production** uses `JSONRenderer()` for machine-parseable structured logs.
- Both structlog-native loggers and stdlib `logging` loggers are routed through the same `ProcessorFormatter`, so all output is consistently structured.
- `merge_contextvars` is included so you can bind per-request context (e.g. `structlog.contextvars.bind_contextvars(user_id=request.user.id)`).
- `django.server` is set to WARNING to suppress routine request logs that `django_structlog.middlewares.RequestMiddleware` already handles in a structured way.

### 5. Usage in application code

```python
import structlog

logger = structlog.get_logger(__name__)

logger.info("order_placed", order_id=order.id, total=order.total)
logger.warning("payment_retry", attempt=3, order_id=order.id)
```

Always use keyword arguments for structured context rather than f-strings or `%`-formatting.
