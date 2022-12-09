import logging


def get_logger(name: str = "logger",          # type: ignore
               file: str = "logs/log.txt",
               level: int = logging.NOTSET):  # type: ignore

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(file)
    fh.setLevel(level)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create formatter and add it to the handlers
    f: str = '%(asctime)s: %(pathname)s %(lineno)d - %(levelname)s - %(message)s'
    formatter = logging.Formatter(f,
                                  datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add the handlers to logger
    if not logger.hasHandlers():
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger


if __name__ == "__main__":
    logger = get_logger()
    logger.error('This should go to both console and file')
