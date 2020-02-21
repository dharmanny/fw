def test_keyword_one(x):
    """Dingen"""
    print('hi', x)
    _testie_func()


def _testie_func():
    print('hihihihihihih')




class TestClass:
    def test_class_keyword_one(self, x, y=4, *args, **kwargs):
        print(x)
        self._intern()

    def _intern(self):
        print('bla')