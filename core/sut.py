from fw.core.keyword import PageObjectModelKeywords
from fw.core.utilities import Util


class SystemInterfaces:
    def __init__(self):
        if Util().settings().INCLUDE_POM:
            self.pom = PageObjectModelKeywords().get_keyword_classes(kw_mode=False)()
