LOG_DEFAULT_HANDLERS = ['filehandler',]
LOG_FORMAT = (
    '%(asctime)s: %(lineno)d - %(name)s - %(funcName)s: '
    '%(levelname)s - %(message)s'
)

# dictConfig логгера
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT,
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'filehandler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': 'app_log.log',
            'mode': 'a',
            'backupCount': 3,
            'maxBytes': 50000,
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        '': {
            'handlers': LOG_DEFAULT_HANDLERS,
            'level': 'DEBUG',
        },
    },
    'root': {
        'level': 'DEBUG',
        'formatter': 'verbose',
        'handlers': LOG_DEFAULT_HANDLERS,
    },
}
