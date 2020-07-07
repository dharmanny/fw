

class Executer:
    def __init__(self, keyword, data):
        self.keyword = keyword
        self.data = data

    def run(self):
        self.data.apply(self._iterate, axis=1)

    def _iterate(self, row):
        self.keyword(**row.to_dict())