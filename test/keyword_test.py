import fw.core.keyword as kw
from pathlib import Path

class TestKeywordsBasic:
    def setup_method(self):
        locs = Path(*Path(__file__).parts[:-1], 'resources', 'keyword_files', 'stub.py')
        self.locations = [locs]
        self.Keywords = kw.Keywords(self.locations)

    def test_all_keywords_type(self):
        error = "Mandatory fields should be returned in a list."
        assert isinstance(self.Keywords.get_all_keywords(), list), error

    def test_mandatory_fields_type(self):
        error = "Mandatory fields should be returned in a list."
        assert isinstance(self.Keywords.get_mandatory_fields('test_kw'), list), error

    def test_optional_fields_type(self):
        error = "Optional fields should be returned in a dict."
        assert isinstance(self.Keywords.get_optional_fields('test_kw'), dict), error

    def test_conditional_fields_type(self):
        error = "Conditional fields should be returned in a dict."
        assert isinstance(self.Keywords.get_conditional_fields('test_kw'), dict), error

    def test_attributes(self):
        error = "The attribute {} is missing."
        assert hasattr(self.Keywords, 'locs'), error.format('locs')
        assert hasattr(self.Keywords, 'kws'), error.format('kws')


class TestKeywordsDiscovery:
    def setup_method(self):
        locs = Path(*Path(__file__).parts[:-1], 'resources', 'keyword_files', 'keywords.py')
        self.locations = [locs]
        self.Keywords = kw.Keywords(self.locations)
        self.kw_names = self.Keywords.get_all_keywords()

    def test_function_keyword(self):
        error = '"new_keyword" not found as keyword'
        assert 'new_keyword' in self.kw_names, error

    def test_function_not_a_keyword(self):
        error = '"_not_a_keyword" was found as keyword'
        assert '_not_a__keyword' not in self.kw_names, error

    def test_class_keyword(self):
        error = '"new_class_keyword" not found as keyword'
        assert 'new_class_keyword' in self.kw_names, error

    def test_class_not_a_keyword(self):
        error = '"_not_a_class_keyword" was found as keyword'
        assert '_not_a_class_keyword' not in self.kw_names, error

    def test_class_attribute(self):
        error = '"x" was found as keyword'
        assert 'x' not in self.kw_names, error