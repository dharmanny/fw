from pathlib import Path
import importlib
import os


class KeywordFiles:
    def __init__(self):
        main_dir = Path(*Path(__file__).parts[:-2])
        kw_dir = Path(main_dir, 'keywords')
        files = []
        mods = []
        for d in os.listdir(kw_dir):
            base = Path(kw_dir, d)
            if 'keywords.py' in os.listdir(base):
                files.append(Path(base, 'keywords.py'))
                mods.append('fw.keywords.{dir}.keywords'.format(dir=d))
        self.kw_files = files
        self.mods = mods
        self.kw_names = self._get_all_names()

    @staticmethod
    def _get_kw_attributes(cls):
        kws = []
        for met in dir(cls):
            attr = getattr(cls, met)
            if callable(attr) and met[0] != '_':
                kws.append(met)
        return kws

    @staticmethod
    def _get_class_attr(mod, cls):
        try:
            return getattr(importlib.import_module(mod), cls)
        except AttributeError:
            return None

    def _get_all_names(self):
        keyword_classes = self.get_keyword_classes()
        config_classes = self.get_config_classes()
        data_classes = self.get_data_classes()
        kws = []
        for kw, conf, dat in zip(keyword_classes, config_classes, data_classes):
            cls_kws = self._get_kw_attributes(kw)
            conf_kws = self._get_kw_attributes(conf)
            dat_kws = self._get_kw_attributes(dat)
            kws.extend(list(set(cls_kws) & set(conf_kws) & set(dat_kws)))
        return kws

    def get_keyword_classes(self):
        return [self._get_class_attr(m, 'Keywords') for m in self.mods]

    def get_config_classes(self):
        return [self._get_class_attr(m, 'Config') for m in self.mods]

    def get_data_classes(self):
        return [self._get_class_attr(m, 'Data') for m in self.mods]


class KeywordMethods(*KeywordFiles().get_keyword_classes()):
    pass


class ConfigMethods(*KeywordFiles().get_config_classes()):
    pass


class DataMethods(*KeywordFiles().get_data_classes()):
    pass


class KeywordArgs(KeywordFiles):
    def get_mandatory_args(self, name):
        if name not in self.kw_names:
            raise AssertionError('The indicated keyword ("{kw}") does not exist.'.format(kw=name))
        try:
            d = getattr(ConfigMethods(), name)
        except AttributeError:
            return []
        return d.get('mandatory_variables', [])


class KeywordQualification(KeywordFiles):
    def get_qualified_keywords(self):
        return self.kw_names
