from fw.core.keyword import KeywordMethods, DataMethods, ConfigMethods
from fw.core.data import DataLoader
from fw.core.conventions import KeywordNameConventions, FileName

import zipfile
from pathlib import Path
import os
import shutil

class Runner:
    def __init__(self, fwo):
        self._fwo = fwo

    @staticmethod
    def _zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                os.chdir(root)
                ziph.write(os.path.relpath(os.path.join(root, file)))

    def run_kw(self, name, args, kwargs):
        fwo = self._fwo
        fwo.DATA = DataLoader(fwo).get_data(name, *args, **kwargs)
        method_name = KeywordNameConventions().convert_name(name, in_name='keyword')
        DataLoader(fwo).validate_data(fwo.DATA, name)
        getattr(DataMethods(), method_name)(fwo)
        getattr(KeywordMethods(), method_name)(fwo)

    def finish_test(self, test_name, evidence_loc):
        base_name = '{}.zip'.format(self._fwo.fw_settings.EVIDENCE_ARCHIVE_NAME)
        archive_name = FileName(base_name).get_filename(test_name=test_name)
        loc = Path(*Path(evidence_loc), archive_name)

        # Create a zip file handler, zip and close the archive
        ziph = zipfile.ZipFile(loc, 'w', zipfile.ZIP_DEFLATED)
        self._zipdir(evidence_loc, ziph)
        ziph.close()

        # go out of the evidence directory and remove it
        os.chdir('..')
        shutil.rmtree(self._fwo.TEST.EVIDENCE_LOC)

