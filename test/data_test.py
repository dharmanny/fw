import unittest as ut
import fw.core.data as dl
import fw
import pandas as pd


class AddSettingsTests(ut.TestCase):
    def setup_methods(self):
        framework = fw.fw(**{'--LOG_LEVEL': None})
        fw.test_settings = pd.Series({'INIT': True})
        self.fw = fw
        self.dl = dl.DataLoader(self.fw)

    def test_only_test_settings(self):
        settings = {'-TESTVAR1': 'VAL1'}
        rest_kwargs = self.dl.add_settings(settings)
        self.assertDictEqual(rest_kwargs, {}, 'All arguments should be consumed')
        self.assertEqual('VAL1', self.fw.test_settings.TESTVAR1, 'Test variable should be included now.')

    def test_test_setting_and_extra(self):
        settings = {'-TESTVAR1': 'VAL1',
                    'Extra': 1}
        rest_kwargs = self.dl.add_settings(settings)
        self.assertDictEqual(rest_kwargs, {'Extra': 1}, 'All arguments should be consumed')
        self.assertEqual('VAL1', self.fw.test_settings.TESTVAR1, 'Test variable should be included now.')

    def test_only_fw_settings(self):
        settings = {'--FWVAR1': 'VAL1'}
        rest_kwargs = self.dl.add_settings(settings)
        self.assertDictEqual(rest_kwargs, {}, 'All arguments should be consumed')
        self.assertEqual('VAL1', self.fw.fw_settings.FWVAR1, 'Framework variable should be included now.')

    def test_fw_setting_and_extra(self):
        settings = {'--FWVAR1': 'VAL1',
                    'Extra': 1}
        rest_kwargs = self.dl.add_settings(settings)
        self.assertDictEqual(rest_kwargs, {'Extra': 1}, 'All arguments should be consumed')
        self.assertEqual('VAL1', self.fw.fw_settings.FWVAR1, 'Framework variable should be included now.')

    def test_fw_and_test_settings_only(self):
        settings = {'-TESTVAR1': 'VAL1',
                    '--FWVAR1': 'VAL2'}
        rest_kwargs = self.dl.add_settings(settings)
        self.assertDictEqual(rest_kwargs, {}, 'All arguments should be consumed')
        self.assertEqual('VAL1', self.fw.test_settings.TESTVAR1, 'Test variable should be included now.')
        self.assertEqual('VAL2', self.fw.fw_settings.FWVAR1, 'Framework variable should be included now.')

    def test_fw_and_test_settings_and_extra(self):
        settings = {'-TESTVAR1': 'VAL1',
                    '--FWVAR1': 'VAL2',
                    'Extra': 1}
        rest_kwargs = self.dl.add_settings(settings)
        self.assertDictEqual(rest_kwargs, {'Extra': 1}, 'All arguments should be consumed')
        self.assertEqual('VAL1', self.fw.test_settings.TESTVAR1, 'Test variable should be included now.')
        self.assertEqual('VAL2', self.fw.fw_settings.FWVAR1, 'Framework variable should be included now.')

    def test_test_settings_with_init(self):
        settings = {'-TESTVAR1': 'VAL1',
                    'Extra': 1}
        with self.assertRaises(AssertionError):
            self.dl.add_settings(settings, init=True)

    def test_no_settings(self):
        settings = {'Extra': 1}
        rest_kwargs = self.dl.add_settings(settings)
        self.assertDictEqual(rest_kwargs, {'Extra': 1}, 'All arguments should be consumed')


