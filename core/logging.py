import os
import logging
from pathlib import Path


class Logging:
    def __init__(self, settings):
        self._settings = settings

    def _get_logging_dir(self):
        try:
            log_loc = self._settings.LOG_LOC
        except AttributeError:
            log_loc = os.getcwd()
        return log_loc

    def _get_logging_level(self):
        try:
            if self._settings.LOG_LEVEL is not None:
                level = getattr(logging, self._settings.LOG_LEVEL.upper())
            else:
                level = None
        except AttributeError:
            level = logging.INFO
        return level

    def _get_log_filename(self):
        try:
            name = self._settings.LOG_NAME
        except AttributeError:
            name = 'fw_logging.log'
        return name

    def set_logging(self):
        log_loc = self._get_logging_dir()
        log_level = self._get_logging_level()
        log_file_name = self._get_log_filename()

        if log_level is not None:
            logging.getLogger().handlers = []                       # reset any possible configurations
            logging.basicConfig(filename=Path(log_loc, log_file_name),
                                filemode='a+',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s \t %(message)s',
                                datefmt='%H:%M:%S',
                                level=log_level)


