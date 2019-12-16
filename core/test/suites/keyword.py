import unittest as ut
import fw.core.keyword as kw
from pathlib import Path
import os
import shutil

class KeywordFilesInitTest(ut.TestCase):
    def setUp(self):
        self.kwf = kw.KeywordFiles()
        self.resource_dir = Path(*Path(__file__).parts[0:-2], 'resources', 'keywords')
        self.kw_dir = Path(*Path(__file__).parts[0:-4], 'keywords')
        for d in os.listdir(self.resource_dir):
            shutil.copytree(Path(self.resource_dir, d), self.kw_dir)

    def tearDown(self):
        for d in os.listdir(self.resource_dir):
            shutil.rmtree(Path(self.resource_dir, d), self.kw_dir)

    def test_positive(self):
        self.assertIn('test_case_1', self.kwf.kw_names, 'test_case_1 should be in the keyword names')
        self.assertIn('test_case_2', self.kwf.kw_names, 'test_case_1 should be in the keyword names')



class KeywordFilesGetKeywordClasses(ut.TestCase):
    pass


class KeywordFilesGetConfigClasses(ut.TestCase):
    pass


class KeywordFilesGetDataClasses(ut.TestCase):
    pass
