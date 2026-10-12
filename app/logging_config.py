import structlog


def configure_logging(env: str = "development") -> None:
    renderer = (
        structlog.processors.JSONRenderer()
        if env == "production"
        else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            renderer,
        ],
        cache_logger_on_first_use=True,
    )