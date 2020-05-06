# een extra comment. Doet nu niets.

from .core import utilities
from .core import logging
from .core import data
from .core import keyword
from .core import library
from .core import sut
from .core import execution
from .core import environment
from .core import authorization


class fw:
    def __init__(self, env=None, **settings):
        util = utilities.Util()
        self.fw_settings = util.settings()
        self.fw_settings, test_sets, settings = util.add_settings(self.fw_settings, {}, settings, init=True)
        self.fw_dir = util.fw_dir()
        self.env = environment.Env().load_environment_settings(util.parse_env(env))
        logging.Logging(self.fw_settings).set_logging()

        self.auth = authorization.Authorization(self)
        self.lib = library.Library(self)
        self.sut = sut.SystemInterfaces(self)

    def get_keyword_names(self):
        return keyword.KeywordInfo().get_qualified_keywords()

    def get_keyword_arguments(self, name: str):
        return keyword.KeywordInfo().get_keyword_arguments(name)

    def get_keyword_documentation(self, name: str):
        return keyword.KeywordInfo().get_keyword_documentation(name)

    def run_keyword(self, name: str, args: list, kwargs: dict):
        return execution.Runner().run_kw(self, name, args, kwargs)


class Debug(fw):
    pass

