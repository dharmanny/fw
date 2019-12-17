from .core import logging as fw_log
from . import settings as s
import fw.core.initiator as init
import fw.core.data as dat
import fw.core.keyword as kw

class Framework:
    def __init__(self, env=None, **settings):
        initiator = init.FrameworkInitiator()
        self.fw_settings = initiator.load_settings_file()
        self.env = initiator.load_environment(env)
        dat.DataLoader(self).add_settings(settings, init=True)
        fw_log.set_logging(self.fw_settings)

    def get_keyword_names(self):
        return kw.KeywordQualification().get_qualified_keywords()