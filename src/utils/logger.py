import logging
import logging.handlers

LOGGER_FORMAT = "%(asctime)s [%(levelname)s] %(module)s: %(message)s"


def init_logging(name: str, level: str) -> None:

    logging.basicConfig(format=LOGGER_FORMAT, datefmt="%Y-%m-%d %H:%M:%S",
                        level=logging.getLevelName(level))


def add_log_handler(logfile: str, level: str) -> None:

    logHandler = logging.handlers.TimedRotatingFileHandler(
        filename=logfile, when="midnight", interval=1, backupCount=14)
    logHandler.setLevel(logging.getLevelName(level))
    logHandler.setFormatter(logging.Formatter(LOGGER_FORMAT))
    logging.getLogger().addHandler(logHandler)
