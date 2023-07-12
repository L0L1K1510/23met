import logging
from datetime import date


def init_logger(name, subname=None):
    logger = logging.getLogger(name)

    current_date = date.today()
    date_string = current_date.strftime('%Y-%m-%d')

    log_path = f"logs/{date_string}.log"

    if subname is not None:
        FORMAT = f"%(asctime)s :: %(name)s.{subname}:%(lineno)s :: %(levelname)s :: %(message)s"
    else:
        FORMAT = "%(asctime)s :: %(name)s:%(lineno)s :: %(levelname)s :: %(message)s"

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(FORMAT))
    fh = logging.FileHandler(filename=log_path)
    fh.setFormatter(logging.Formatter(FORMAT))
    logger.setLevel(logging.DEBUG)
    sh.setLevel(logging.DEBUG)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(sh)
    logger.addHandler(fh)

    return logger