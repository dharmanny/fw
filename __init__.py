from .Core import logging as fw_log
from . import settings as s
import Fw.Core.Initiator as Init
import Fw.Core.data_loader as data

class Framework:
    def __init__(self, env=None, **settings):
        initiator = Init.FrameworkInitiator()
        self.fw_settings = initiator.load_settings_file()
        self.env = initiator.load_environment(env)
        data.DataLoader(self).add_settings(settings, init=True)
        fw_log.set_logging(self.fw_settings)