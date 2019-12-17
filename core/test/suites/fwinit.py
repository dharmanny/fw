import unittest as ut
from pathlib import Path
import os
import shutil
from fw import Framework


class InitTest(ut.TestCase):
    def setUp(self):
        self.resource_dir = Path(*Path(__file__).parts[0:-2], 'resources', 'fwinit')
        self.env_dir = Path(*Path(__file__).parts[0:-4], 'env')
        self.env_files = [f for f in os.listdir(self.resource_dir)]
        for file in self.env_files:
            shutil.copy(Path(self.resource_dir, file), Path(self.env_dir, file))

    def test_no_args(self):
        Framework()

    def test_with_fw_settings(self):
        settings = {'--FWSETTING': 'test_text'}
        fw = Framework(**settings)
        self.assertEqual('test_text', fw.fw_settings.FWSETTING, 'The variable should be loaded as env variable')

    def test_with_test_settings(self):
        settings = {'-TESTSETTING': 'test_text'}
        with self.assertRaises(AssertionError):
            Framework(**settings)

    def test_env(self):
        fw = Framework('Test_Env_1')
        self.assertEqual(1, fw.env.TEST_VAR_INT, 'Should be an environment variable.')
        self.assertEqual(True, fw.env.TEST_VAR_BOOL, 'Should be an environment variable.')
        self.assertEqual('Test', fw.env.TEST_VAR_STR, 'Should be an environment variable.')
        self.assertEqual('Test_Env_1', fw.env.ENV_NAME, 'Should be an environment variable.')


class GetKeywordNamesTest(ut.TestCase):
    def setUp(self):
        self.resource_dir = Path(*Path(__file__).parts[0:-2], 'resources', 'fwinit')
        self.kw_dir = Path(*Path(__file__).parts[0:-4], 'keywords')
        for d in os.listdir(self.resource_dir):
            shutil.copytree(Path(self.resource_dir, d), Path(self.kw_dir, d))
        self.fwo = Framework()

    def tearDown(self):
        for d in os.listdir(self.resource_dir):
            shutil.rmtree(Path(self.kw_dir, d))

    def test_keyword_present(self):
        self.assertIn('test_case_1', self.fwo.get_keyword_names(), 'Keyword should be present')
