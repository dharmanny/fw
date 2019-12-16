from .core import logging as fw_log
from . import settings as s
import fw.core.initiator as init
import fw.core.data as data


class Framework:
    def __init__(self, env=None, **settings):
        initiator = init.FrameworkInitiator()
        self.fw_settings = initiator.load_settings_file()
        self.env = initiator.load_environment(env)
        data.DataLoader(self).add_settings(settings, init=True)
        fw_log.set_logging(self.fw_settings)
