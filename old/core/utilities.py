import pandas as pd
from pathlib import Path
import re
import logging


class Util:
    @staticmethod
    def fw_dir():
        return Path(*Path(__file__).parts[:-2])

    def _python_settings(self):
        import fw.old.settings as sets
        return {s.upper(): getattr(sets, s) for s in dir(sets) if s[0] != '_'}

    def _yaml_settings(self, file=None):
        import yaml
        if file is None:
            file = Path(self.fw_dir(), "settings.yaml")
        with open(file, 'r') as stream:
            try:
                set_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise AssertionError('The settings file could not be parsed correctly. '
                                     'The following errors occurred:\n{}'.format(exc))
        for k, v in set_dict.items():
            if isinstance(v, list):
                set_dict[k] = tuple(v)
        return set_dict

    def _get_default_settings(self):
        default = self._yaml_settings(Path(self.fw_dir(), "core", "defaults.yaml"))
        return default

    def settings(self):
        try:
            set_dict = self._yaml_settings()
        except FileNotFoundError:
            set_dict = self._python_settings()
        sets = pd.Series(set_dict)
        def_sets = self._get_default_settings()

        edit_cols = tuple(set(sets.index) & set(def_sets.keys()))
        new_cols = {col: val for col, val in def_sets.items() if col not in edit_cols}
        sets = sets.append(pd.Series(new_cols))

        return sets

    @staticmethod
    def parse_env(env):
        if env is None:
            return env
        elif isinstance(env, str):
            return tuple(re.split(r'[.]|/|\\|:',env))
        else:
            return tuple([str(env)])

    @staticmethod
    def add_settings(fw_settings, test_settings,  kwargs, init=False):
        fw_sets = {k: v for k, v in kwargs.items() if k[0:2] == '--'}
        for st, val in fw_sets.items():
            kwargs.pop(st)
            fw_settings[st.upper()[2:]] = val
            logging.info('Added fw_setting "{s}" with value "{v}"'.format(s=st, v=val))

        test_sets = {k: v for k, v in kwargs.items() if k[0] == '-'}
        if not init:
            for st, val in test_sets.items():
                kwargs.pop(st)
                test_settings[st.upper()[1:]] = val
                logging.info('Added test_setting "{s}" with value "{v}"'.format(s=st, v=val))

        elif len(test_sets) > 0:
            msg = 'Test variables were imported during initiation of the Framework. This is not supported'
            logging.error(msg)
            raise AssertionError(msg)

        for k, v in kwargs.items():
            logging.debug('Returned variable to caller: "{k}", "{v}".'.format(k=k, v=v))

        return fw_settings, test_settings, kwargs
