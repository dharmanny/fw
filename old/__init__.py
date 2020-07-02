from fw.old.core import utilities
from fw.old.core import logging
from fw.old.core import keyword
from fw.old.core import library
from fw.old.core import sut
from fw.old.core import execution
from fw.old.core import environment
from fw.old.core import authorization


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

