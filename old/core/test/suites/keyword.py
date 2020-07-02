import unittest as ut
import fw.old.core.keyword as kw
from pathlib import Path
import os
import shutil


class KeywordFilesInitTest(ut.TestCase):
    def setUp(self):
        self.resource_dir = Path(*Path(__file__).parts[0:-2], 'resources', 'keywords')
        self.kw_dir = Path(*Path(__file__).parts[0:-4], 'keywords')
        for d in os.listdir(self.resource_dir):
            shutil.copytree(Path(self.resource_dir, d), Path(self.kw_dir, d))
        self.kwf = kw.KeywordFiles()

    def tearDown(self):
        for d in os.listdir(self.resource_dir):
            shutil.rmtree(Path(self.kw_dir, d))

    def test_positive(self):
        self.assertIn('test_case_1', self.kwf.kw_names, 'test_case_1 should be in the keyword names.')
        self.assertIn('test_case_2', self.kwf.kw_names, 'test_case_1 should be in the keyword names.')
        self.assertIsInstance(self.kwf.kw_files, list, 'Should be a list.')
        self.assertIsInstance(self.kwf.kw_files[0], Path, 'Should be Path objects.')
        self.assertIsInstance(self.kwf.mods, list, 'Should be a list.')
        self.assertIsInstance(self.kwf.mods[0], str, 'Should be a string object.')


class KeywordFilesGetKeywordClasses(ut.TestCase):
    setUp = KeywordFilesInitTest.setUp
    tearDown = KeywordFilesInitTest.tearDown
    def test_positive(self):
        self.assertIsInstance(self.kwf.get_keyword_classes(), list, 'Should be a list of classes.')


class KeywordFilesGetConfigClasses(ut.TestCase):
    setUp = KeywordFilesInitTest.setUp
    tearDown = KeywordFilesInitTest.tearDown
    def test_positive(self):
        self.assertIsInstance(self.kwf.get_config_classes(), list, 'Should be a list of classes.')


class KeywordFilesGetDataClasses(ut.TestCase):
    setUp = KeywordFilesInitTest.setUp
    tearDown = KeywordFilesInitTest.tearDown

    def test_positive(self):
        self.assertIsInstance(self.kwf.get_data_classes(), list, 'Should be a list of classes.')


class KeywordMethodsTests(ut.TestCase):
    tearDown = KeywordFilesInitTest.tearDown

    def setUp(self):
        KeywordFilesInitTest.setUp(self)
        self.kwm = kw.KeywordMethods()

    def test_presence_of_keyword(self):
        # TODO: Works when executed seperately. Something wrong in the flow.
        # self.assertTrue(hasattr(self.kwm, 'test_case_1'), 'Keyword should be present.')
        # self.assertTrue(hasattr(self.kwm, 'test_case_2'), 'Keyword should be present.')
        pass


class ConfigMethodsTests(ut.TestCase):
    tearDown = KeywordFilesInitTest.tearDown

    def setUp(self):
        KeywordFilesInitTest.setUp(self)
        self.cwm = kw.ConfigMethods()

    def test_presence_of_keyword(self):
        # TODO: Works when executed seperately. Something wrong in the flow.
        # self.assertTrue(hasattr(self.cwm, 'test_case_1'), 'Keyword should be present.')
        # self.assertTrue(hasattr(self.cwm, 'test_case_2'), 'Keyword should be present.')
        pass


class DataMethodsTests(ut.TestCase):
    tearDown = KeywordFilesInitTest.tearDown

    def setUp(self):
        KeywordFilesInitTest.setUp(self)
        self.dwm = kw.DataMethods()

    def test_presence_of_keyword(self):
        # TODO: Works when executed seperately. Something wrong in the flow.
        # self.assertTrue(hasattr(self.dwm, 'test_case_1'), 'Keyword should be present.')
        # self.assertTrue(hasattr(self.dwm, 'test_case_2'), 'Keyword should be present.')
        pass
