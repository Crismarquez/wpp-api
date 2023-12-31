import os
from pathlib import Path
import sys
import logging
import logging.config
from rich.logging import RichHandler
from dotenv import dotenv_values, load_dotenv


BASE_DIR = Path(__file__).parent.parent.absolute()
CONFIG_DIR = Path(BASE_DIR, "config")
DATA_DIR = Path(BASE_DIR, "data")
LOGS_DIR = Path(BASE_DIR, "logs")

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR/ ".env")
ENV_VARIABLES = {
    **dotenv_values(BASE_DIR/ ".env"),  # load environment variables from .env file
    **os.environ,  # override loaded values with environment variables
}

users_allowed = {
    "573127423350": "Cristian",
    "573147731722": "Edward",
}

media_types = {
    'audio/aac': 'aac',
    'audio/mp4': 'mp4',
    'audio/mpeg': 'mp3',
    'audio/amr': 'amr',
    'audio/ogg': 'ogg',
    'text/plain': 'txt',
    'application/pdf': 'pdf',
    'application/vnd.ms-powerpoint': 'ppt',
    'application/msword': 'doc',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'image/jpeg': 'jpeg',
    'image/png': 'png',
    'video/mp4': 'mp4',
    'video/3gp': '3gp',
    'image/webp': 'webp',
}

stickers = {
    "poyo_feliz": 984778742532668,
    "perro_traje": 1009219236749949,
    "perro_triste": 982264672785815,
    "pedro_pascal_love": 801721017874258,
    "pelfet": 3127736384038169,
    "anotado": 24039533498978939,
    "gato_festejando": 1736736493414401,
    "okis": 268811655677102,
    "cachetada": 275511571531644,
    "gato_juzgando": 107235069063072,
    "chicorita": 3431648470417135,
    "gato_triste": 210492141865964,
    "gato_cansado": 1021308728970759
}


# Logger
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "minimal": {"format": "%(message)s"},
        "detailed": {
            "format": "%(levelname)s %(asctime)s [%(name)s:%(filename)s:%(funcName)s:%(lineno)d]\n%(message)s\n"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "minimal",
            "level": logging.DEBUG,
        },
        "info": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGS_DIR, "info.log"),
            "maxBytes": 10485760,  # 1 MB
            "backupCount": 10,
            "formatter": "detailed",
            "level": logging.INFO,
        },
        "error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGS_DIR, "error.log"),
            "maxBytes": 10485760,  # 1 MB
            "backupCount": 10,
            "formatter": "detailed",
            "level": logging.ERROR,
        },
    },
    "root": {
        "handlers": ["console", "info", "error"],
        "level": logging.INFO,
        "propagate": True,
    },
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger()
logger.handlers[0] = RichHandler(markup=True)