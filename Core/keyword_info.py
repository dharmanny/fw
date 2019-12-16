from pathlib import Path

class KeywordInfo:
    def __init__(self, fw):
        main_dir = Path(*Path(__file__).parts[:-2])
        self._kw_dir = Path(main_dir, 'Keywords')
        self._fw = fw

    def get_keyword_names(self):
        pass

    def get_keyword_arguments(self):
        pass

    def get_keyword_example(self):
        pass

    def get_documentation(self):
        pass


