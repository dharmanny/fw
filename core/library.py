from fw.core.datetime import DateParser
from fw.core.data import DataLibrary


class LibBuilder:
    @staticmethod
    def get_lib_classes():
        return []


class Library(DateParser,
              DataLibrary,
              *LibBuilder().get_lib_classes()):
    def __init__(self, fwo, *args):
        DataLibrary.__init__(self, fwo)
        DateParser.__init__(self, *args)
