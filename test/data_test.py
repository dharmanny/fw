import fw.core.data as dat
import fw.core.keyword as kw
import fw.core.settings as sets
from pathlib import Path
import pandas as pd
import pytest


class Helpers:
    def get_loader(self, locs=None):
        if locs is None:
            locs = [Path(*Path(__file__).parts[:-1], 'resources', 'data_tests', 'keywords_1.py')]
        sets.update_settings(LOCATIONS=locs)
        self.keywords = kw.Keywords()
        self.data_loader = dat.DataLoader(self.keywords)

    def basic_dataframe_test(self, data, length, cols, not_cols=()):
        assert isinstance(data, pd.DataFrame), 'The returned data is not a valid pandas.DataFrame type'
        assert len(data) == length, 'The lenght of the data was not correct.'
        for col in cols:
            assert col in data.columns, 'The columns {} was not present as a column but was expected.'.format(col)
        for col in not_cols:
            assert col not in data.columns, 'The columns {} was present as a column but was not expected.'.format(col)


class TestBasics(Helpers):
    def setup_method(self):
        self.get_loader()

    def test_args_in_list(self):
        data = self.data_loader.get_data('keyword_1', 123)
        self.basic_dataframe_test(data, 1, ['X'])
        assert data.X[0] == 123, 'The content of the data was incorrect.'

    def test_args_in_dict(self):
        data = self.data_loader.get_data('keyword_1', X=123)
        self.basic_dataframe_test(data, 1, ['X'])
        assert data.X[0] == 123, 'The content of the data was incorrect.'

    def test_multiple_arguments_in_dict(self):
        data = self.data_loader.get_data('keyword_1', X=123, Y=456)
        self.basic_dataframe_test(data, 1, ['X', 'Y'])
        assert data.X[0] == 123, 'The content of the data was incorrect.'
        assert data.Y[0] == 456, 'The content of the data was incorrect.'

    def test_csv(self):
        csv = Path(*Path(__file__).parts[:-1], 'resources', 'data_tests', 'sample_csv_1.csv')
        data = self.data_loader.get_data('keyword_1', DATA_FILE=csv)
        self.basic_dataframe_test(data, 3, ['X', 'Y', 'Z'], ['DATA_FILE'])
        assert data.X.to_list() == [1, 4, 7], 'The content of the data was incorrect.'
        assert data.Y.to_list() == [2, 5, 8], 'The content of the data was incorrect.'
        assert data.Z.to_list() == [3, 6, 9], 'The content of the data was incorrect.'

    def test_data_with_arguments(self):
        old_data = pd.DataFrame({'X': [1, 4], 'Y': [2, 5]})
        data = self.data_loader.get_data('keyword_1', DATA=old_data, Z=3)
        self.basic_dataframe_test(data, 2, ['X', 'Y', 'Z'], ['DATA'])
        assert data.X.to_list() == [1, 4], 'The content of the data was incorrect.'
        assert data.Y.to_list() == [2, 5], 'The content of the data was incorrect.'
        assert data.Z.to_list() == [3, 3], 'The content of the data was incorrect.'

    def test_add_settings(self):
        sets.update_settings(SETTING_PREFIX='-')
        sets.update_settings(EVAL_INDICATOR='not_test_eval:')
        assert sets.EVAL_INDICATOR == 'not_test_eval:', 'The setup was not done correctly'
        data = self.data_loader.get_data('keywords_1', X=1, Y=2, **{'-EVAL_INDICATOR': 'test_eval:'})
        self.basic_dataframe_test(data, 1, ['X', 'Y'], ['-EVAL_INDICATOR'])
        assert sets.EVAL_INDICATOR == 'test_eval:', 'The setting was not passed correctly'

    def test_no_data(self):
        data = self.data_loader.get_data('keywords_2')
        assert data is None, 'Data was passed, while it should have been None'

    def test_no_data_with_settings(self):
        sets.update_settings(SETTING_PREFIX='-')
        sets.update_settings(EVAL_INDICATOR='not_test_eval:')
        assert sets.EVAL_INDICATOR == 'not_test_eval:', 'The setup was not done correctly'
        data = self.data_loader.get_data('keywords_2', **{'-EVAL_INDICATOR': 'test_eval:'})
        assert data is None, 'Data was passed, while it should have been None'
        assert sets.EVAL_INDICATOR == 'test_eval:', 'The setting was not passed correctly'


class TestEvaluation(Helpers):
    def setup_method(self):
        self.get_loader()
        self.eval = 'ev:'
        sets.update_settings(EVAL_INDICATOR=self.eval)
        assert sets.EVAL_INDICATOR == self.eval, 'Setup went wrong'

    def test_basic_calculations(self):
        x = 123
        y = 456
        z = '{}X+Y'.format(self.eval)
        data = self.data_loader.get_data('keyword_2', X=x, Y=y, Z=z)
        self.basic_dataframe_test(data, 1, ['X', 'Y', 'Z'])
        assert data.Z[0] == 579, 'The cells where not evaluated correctly'

    def test_basic_string_concats(self):
        x = '123'
        y = '456'
        z = '{}X+Y'.format(self.eval)
        data = self.data_loader.get_data('keyword_2', X=x, Y=y, Z=z)
        self.basic_dataframe_test(data, 1, ['X', 'Y', 'Z'])
        assert data.Z[0] == '123456', 'The cells where not evaluated correctly'

    def test_basic_function(self):
        x = '123'
        y = '456'
        z = '{}X.replace("2", " ")+Y'.format(self.eval)
        data = self.data_loader.get_data('keyword_2', X=x, Y=y, Z=z)
        self.basic_dataframe_test(data, 1, ['X', 'Y', 'Z'])
        assert data.Z[0] == '1 3456', 'The cells where not evaluated correctly'

    def test_layered_evaluation(self):
        x = '123'
        y = '{}X + "abc"'.format(self.eval)
        z = '{}Y.replace("2", " ")'.format(self.eval)
        data = self.data_loader.get_data('keyword_2', X=x, Y=y, Z=z)
        self.basic_dataframe_test(data, 1, ['X', 'Y', 'Z'])
        assert data.Z[0] == '1 3abc', 'The cells where not evaluated correctly'

    def test_evaluation_multiple_rows(self):
        csv = Path(*Path(__file__).parts[:-1], 'resources', 'data_tests', 'sample_csv_1.csv')
        a = '{}Z+Y'.format(self.eval)
        data = self.data_loader.get_data('keyword_1', DATA_FILE=csv, A=a)
        self.basic_dataframe_test(data, 3, ['X', 'Y', 'Z', 'A'])
        assert data.A[0] == 5, 'The cells where not evaluated correctly'
        assert data.A[1] == 11, 'The cells where not evaluated correctly'
        assert data.A[2] == 17, 'The cells where not evaluated correctly'


class TestFiltering(Helpers):

    def setup_method(self):
        self.get_loader()
        self.eval = 'ev:'
        sets.update_settings(EVAL_INDICATOR=self.eval)
        assert sets.EVAL_INDICATOR == self.eval, 'Setup went wrong'

    def test_row_selection_list(self):
        csv = Path(*Path(__file__).parts[:-1], 'resources', 'data_tests', 'sample_csv_2.csv')
        data = self.data_loader.get_data('keyword_1', DATA_FILE=csv, ROWS='0, 1, 4')
        self.basic_dataframe_test(data, 3, ['X', 'Y', 'Z'], ['ROWS'])
        assert data.index.to_list() == [0, 1, 4], 'Incorrect rows where returned (check was done based on index)'

    def test_row_selection_none(self):
        csv = Path(*Path(__file__).parts[:-1], 'resources', 'data_tests', 'sample_csv_2.csv')
        data = self.data_loader.get_data('keyword_1', DATA_FILE=csv, ROWS='None')
        self.basic_dataframe_test(data, 7, ['X', 'Y', 'Z'], ['ROWS'])
        assert data.index.to_list() == [0, 1, 2, 3, 4, 5, 6], 'Incorrect rows where returned (check was done based ' \
                                                              'on index)'

    def test_row_selection_all(self):
        csv = Path(*Path(__file__).parts[:-1], 'resources', 'data_tests', 'sample_csv_2.csv')
        data = self.data_loader.get_data('keyword_1', DATA_FILE=csv, ROWS='All')
        self.basic_dataframe_test(data, 7, ['X', 'Y', 'Z'], ['ROWS'])
        assert data.index.to_list() == [0, 1, 2, 3, 4, 5, 6], 'Incorrect rows where returned (check was done based ' \
                                                              'on index)'

    def test_row_selection_invalid(self):
        csv = Path(*Path(__file__).parts[:-1], 'resources', 'data_tests', 'sample_csv_2.csv')
        with pytest.raises(ValueError) as excinfo:
            self.data_loader.get_data('keyword_1', DATA_FILE=csv, ROWS='Invalid_value')
        assert "The passed row value could not be interpreted " \
               "as row selection." == str(excinfo.value), 'Incorrect error was raised'

    def test_index_too_high(self):
        csv = Path(*Path(__file__).parts[:-1], 'resources', 'data_tests', 'sample_csv_2.csv')
        with pytest.raises(ValueError) as excinfo:
            self.data_loader.get_data('keyword_1', DATA_FILE=csv, ROWS='7')
        assert 'The resulting rows where not present in the ' \
               'actual data.' == str(excinfo.value), 'Incorrect error was raised'

    def test_index_partially_too_high(self):
        csv = Path(*Path(__file__).parts[:-1], 'resources', 'data_tests', 'sample_csv_2.csv')
        with pytest.raises(ValueError) as excinfo:
            self.data_loader.get_data('keyword_1', DATA_FILE=csv, ROWS='6, 7')
        assert 'The resulting rows where not present in the ' \
               'actual data.' == str(excinfo.value), 'Incorrect error was raised'

    def test_with_basic_eval(self):
        csv = Path(*Path(__file__).parts[:-1], 'resources', 'data_tests', 'sample_csv_1.csv')
        rows = '{} X > 3'.format(self.eval)
        data = self.data_loader.get_data('keyword_1', DATA_FILE=csv, ROWS=rows)
        self.basic_dataframe_test(data, 2, ['X', 'Y', 'Z'], ['ROWS'])
        assert data.index.to_list() == [1, 2], 'Incorrect rows where returned (check was done based on index)'

    def test_with_invalid_row_evaluation(self):
        csv = Path(*Path(__file__).parts[:-1], 'resources', 'data_tests', 'sample_csv_1.csv')
        rows = '{} X + 3'.format(self.eval)
        with pytest.raises(AssertionError) as excinfo:
            self.data_loader.get_data('keyword_1', DATA_FILE=csv, ROWS=rows)
        assert "inclusion (True) or exclusion (False)" in str(excinfo.value), 'Incorrect error message was raised'





# class AddSettingsTests(ut.TestCase):
#     def setup_methods(self):
#         framework = fw.fw(**{'--LOG_LEVEL': None})
#         fw.test_settings = pd.Series({'INIT': True})
#         self.fw = fw
#         self.dl = dl.DataLoader(self.fw)
#
#     def test_only_test_settings(self):
#         settings = {'-TESTVAR1': 'VAL1'}
#         rest_kwargs = self.dl.add_settings(settings)
#         self.assertDictEqual(rest_kwargs, {}, 'All arguments should be consumed')
#         self.assertEqual('VAL1', self.fw.test_settings.TESTVAR1, 'Test variable should be included now.')
#
#     def test_test_setting_and_extra(self):
#         settings = {'-TESTVAR1': 'VAL1',
#                     'Extra': 1}
#         rest_kwargs = self.dl.add_settings(settings)
#         self.assertDictEqual(rest_kwargs, {'Extra': 1}, 'All arguments should be consumed')
#         self.assertEqual('VAL1', self.fw.test_settings.TESTVAR1, 'Test variable should be included now.')
#
#     def test_only_fw_settings(self):
#         settings = {'--FWVAR1': 'VAL1'}
#         rest_kwargs = self.dl.add_settings(settings)
#         self.assertDictEqual(rest_kwargs, {}, 'All arguments should be consumed')
#         self.assertEqual('VAL1', self.fw.fw_settings.FWVAR1, 'Framework variable should be included now.')
#
#     def test_fw_setting_and_extra(self):
#         settings = {'--FWVAR1': 'VAL1',
#                     'Extra': 1}
#         rest_kwargs = self.dl.add_settings(settings)
#         self.assertDictEqual(rest_kwargs, {'Extra': 1}, 'All arguments should be consumed')
#         self.assertEqual('VAL1', self.fw.fw_settings.FWVAR1, 'Framework variable should be included now.')
#
#     def test_fw_and_test_settings_only(self):
#         settings = {'-TESTVAR1': 'VAL1',
#                     '--FWVAR1': 'VAL2'}
#         rest_kwargs = self.dl.add_settings(settings)
#         self.assertDictEqual(rest_kwargs, {}, 'All arguments should be consumed')
#         self.assertEqual('VAL1', self.fw.test_settings.TESTVAR1, 'Test variable should be included now.')
#         self.assertEqual('VAL2', self.fw.fw_settings.FWVAR1, 'Framework variable should be included now.')
#
#     def test_fw_and_test_settings_and_extra(self):
#         settings = {'-TESTVAR1': 'VAL1',
#                     '--FWVAR1': 'VAL2',
#                     'Extra': 1}
#         rest_kwargs = self.dl.add_settings(settings)
#         self.assertDictEqual(rest_kwargs, {'Extra': 1}, 'All arguments should be consumed')
#         self.assertEqual('VAL1', self.fw.test_settings.TESTVAR1, 'Test variable should be included now.')
#         self.assertEqual('VAL2', self.fw.fw_settings.FWVAR1, 'Framework variable should be included now.')
#
#     def test_test_settings_with_init(self):
#         settings = {'-TESTVAR1': 'VAL1',
#                     'Extra': 1}
#         with self.assertRaises(AssertionError):
#             self.dl.add_settings(settings, init=True)
#
#     def test_no_settings(self):
#         settings = {'Extra': 1}
#         rest_kwargs = self.dl.add_settings(settings)
#         self.assertDictEqual(rest_kwargs, {'Extra': 1}, 'All arguments should be consumed')


