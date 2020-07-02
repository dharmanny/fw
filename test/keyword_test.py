import fw.core.keyword as kw


class TestKeywords:
    def setup_method(self):
        locations = []
        self.Keywords = kw.Keywords(locations)

    def test_mandatory_fields_type(self):
        error = "Mandatory fields should be returned in a list."
        assert isinstance(self.Keywords.get_mandatory_fields('testname'), list), error

    def test_optional_fields_type(self):
        error = "Optional fields should be returned in a list."
        assert isinstance(self.Keywords.get_mandatory_fields('testname'), list), error

    def test_conditional_fields_type(self):
        error = "Conditional fields should be returned in a dict."
        assert isinstance(self.Keywords.get_conditional_fields('testname'), dict), error
