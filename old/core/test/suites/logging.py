import pandas as pd
import fw.old.core.logging as lg
import logging
import unittest as ut
import os
from pathlib import Path

class SetLogginTest(ut.TestCase):
    def setUp(self):
        self.temp_dir = Path(*Path(__file__).parts[0:-2], 'temp')
        self.settings = pd.Series({'LOG_LOC': self.temp_dir,
                                   'LOG_LEVEL': None,
                                   'LOG_NAME': 'test.log'})

    def test_change_name(self):
        self.settings['LOG_NAME'] = 'test_change_name.log'
        self.settings['LOG_LEVEL'] = 'INFO'
        old_handles = logging.getLogger().handlers
        logging.getLogger().handlers = []
        lg.set_logging(self.settings)
        logging.getLogger().handlers = old_handles
        self.assertIn('test_change_name.log', os.listdir(self.temp_dir), 'The file should be present.')

    def test_invalid_log_level(self):
        self.settings['LOG_LEVEL'] = 'INVALID_LEVEL'
        old_handles = logging.getLogger().handlers
        logging.getLogger().handlers = []
        lg.set_logging(self.settings)
        logging.getLogger().handlers = old_handles
        self.assertIn('INFO', str(logging.getLogger()),
                      'In case of an invalid logging level, it should default to INFO')

    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(Path(self.temp_dir, f))
