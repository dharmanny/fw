from fw.old.core import DateParser
from fw.old.core import DataLibrary


class LibBuilder:
    @staticmethod
    def get_lib_classes():
        return []


class Library(DateParser,
              DataLibrary,
              *LibBuilder().get_lib_classes()):
    pass
