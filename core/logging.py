import os
import logging
from pathlib import Path

def set_logging(settings):
    try:
        log_loc = settings.LOG_LOC
    except AttributeError:
        log_loc = os.getcwd()

    try:
        if settings.LOG_LEVEL is not None:
            level = getattr(logging, settings.LOG_LEVEL.upper())
        else:
            level = None
    except AttributeError:
        level = logging.INFO

    try:
        name = settings.LOG_NAME
    except AttributeError:
        name = 'fw_logging.log'


    if level is not None:
        logging.getLogger().handlers = []                       # reset any possible configurations
        logging.basicConfig(filename=Path(log_loc, name),
                            filemode='a+',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s \t %(message)s',
                            datefmt='%H:%M:%S',
                            level=level)

