from fw.core.datetime import DateParser
from fw.core.data import DataLibrary


class LibBuilder:
    @staticmethod
    def get_lib_classes():
        return []


class Library(DateParser,
              DataLibrary,
              *LibBuilder().get_lib_classes()):
    pass
