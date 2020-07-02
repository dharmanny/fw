from fw.old.core import PageObjectModelKeywords
from fw.old.core import Util


class SutParser:


    def get_lib_classes():
        return []


class SystemInterfaces:
    def __init__(self, fwo):
        if Util().settings().INCLUDE_POM:
            self.pom = PageObjectModelKeywords().get_keyword_classes(kw_mode=False)()


