import unittest as ut
from pathlib import Path
import os
import shutil
from fw.core.initiator import FrameworkInitiator as fi


class GetEnvModNameTest(ut.TestCase):
    def setUp(self):
        self.resource_dir = Path(*Path(__file__).parts[0:-2], 'resources', 'initiator')
        self.env_dir = Path(*Path(__file__).parts[0:-4], 'env')
        self.env_files = [f for f in os.listdir(self.resource_dir)]
        self.fi = fi()
        for file in self.env_files:
            shutil.copy(Path(self.resource_dir, file), Path(self.env_dir, file))

    def test_positive(self):
        mod = self.fi._get_env_mod_name('Test_Env_1', self.env_files)
        self.assertEqual(mod, 'fw.env.Test_Env_1', 'The module name should have been returned.')

    def test_negative(self):
        with self.assertRaises(ImportError):
            self.fi._get_env_mod_name('Not_existing_file', self.env_files)

    def tearDown(self):
        for file in os.listdir(self.resource_dir):
            os.remove(Path(self.env_dir, file))

class GetEnvFilesTest(ut.TestCase):
    def setUp(self):
        GetEnvModNameTest.setUp(self)

    def test_positive(self):
        valid_envs = [f for f in self.env_files if (f[0] != '_') and ('.py' in f)]
        for file in valid_envs:
            self.assertIn(file, self.fi._get_env_files(), 'Environment should be returned.')

    def test_no_valid_env_files(self):
        self.assertIn('_invalid_env.py', self.env_files)
        self.assertNotIn('_invalid_env.py', self.fi._get_env_files(), 'Environment should not be returned.')


class LoadEnvironmentTests(ut.TestCase):
    def setUp(self):
        GetEnvModNameTest.setUp(self)

    def test_get_supplied_env(self):
        act = self.fi.load_environment('Test_Env_1')
        self.assertEqual(1, act.TEST_VAR_INT, 'Should be an environment variable.')
        self.assertEqual(True, act.TEST_VAR_BOOL, 'Should be an environment variable.')
        self.assertEqual('Test', act.TEST_VAR_STR, 'Should be an environment variable.')
        self.assertEqual('Test_Env_1', act.ENV_NAME, 'Should be an environment variable.')

    def test_load_none(self):
        act = self.fi.load_environment(None)
        self.assertEqual(None, act.ENV_NAME, 'Should be an environment variable.')
        self.assertEqual(1, len(act), 'There should be only one environment variable.')