
class Keywords:
    def test_case_1(self, fw):
        """ This is a dummy keyword """
        pass

    def test_case_2(self, fw):
        """ This is a dummy keyword """
        pass



class Config:
    @staticmethod
    def test_case_1():
        mandatory = ['var2', 'var3']
        return {'mandatory_variables': mandatory,
                'iterable': 'R'}

    @staticmethod
    def test_case_2():
        mandatory = ['var2', 'var3']
        return {'mandatory_variables': mandatory,
                'iterable': 'R'}


class Data:
    def test_case_1(self, fw):
        pass

    def test_case_2(self, fw):
        pass
