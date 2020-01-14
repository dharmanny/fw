import pandas as pd

class Keywords:
    def test_1(self, fw):
        """Stuff this keyword does"""
        pass


class Config:
    @staticmethod
    def test_1():
        """ This is a dummy keyword """
        mandatory = ['var2', 'var3']
        return {'mandatory_variables': mandatory,
                'iterable': 'R'}


class Data:
    def test_1(self, fw):
        pass
