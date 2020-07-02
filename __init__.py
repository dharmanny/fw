

class fw:
    def __init__(self, env=None, **settings):
        pass

    def get_keyword_names(self):
        return []

    def get_keyword_arguments(self, name: str):
        return []

    def get_keyword_documentation(self, name: str):
        return ''

    def run_keyword(self, name: str, args: list, kwargs: dict):
        pass
