import pandas as pd
from pathlib import Path

class Keywords:
    def test_1(self, fw):
        """Stuff this keyword does"""
        print('blabla')


class Config:
    @staticmethod
    def test_1():
        """ This is a dummy keyword """
        mandatory = ['var2', 'var3']
        return {'mandatory_variables': mandatory,
                'iterable': 'table'}


class Data:
    def test_1(self, fw):
        pass
