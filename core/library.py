# import fw.settings as sets
from fw.core.datetime import DateParser


class LibBuilder:
    @staticmethod
    def get_lib_classes():
        return []


class Library(DateParser, *LibBuilder().get_lib_classes()):
    pass
