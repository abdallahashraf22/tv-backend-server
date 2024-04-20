LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            # exact format is not important, this is the minimum information
            "()": "uvicorn.logging.ColourizedFormatter",
            "format": "{levelprefix} {name}|{asctime}:{message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        }
    },
    "handlers": {
        "info_filter": {
            "level": "INFO",
            "class": "utils.log_utils.custom_logs_class.TimelyRotatingFileHandler",
            "log_title": "app.log",  # Adjust the path as needed
            "when_to": "midnight",  # rotate every midnight utc
            "intervals": 1,
            "backupCount": 7,
            "formatter": "default",
        },
        "warning_filter": {
            "level": "WARNING",
            "class": "utils.log_utils.custom_logs_class.TimelyRotatingFileHandler",
            "log_title": "error.log",
            "when_to": "midnight",
            "intervals": 1,
            "backupCount": 7,
            "formatter": "default",
        },
        # console logs to stderr
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        # default for all undefined Python modules
        # Our application code
        "": {
            "level": "INFO",
            "handlers": ["console", "info_filter", "warning_filter"],
            # Avoid double logging because of root logger
            "propagate": False,
        }
    },
}
