import Fw.settings as sets
import pandas as pd
import os
import importlib
from pathlib import Path

class FrameworkInitiator:

    @staticmethod
    def _get_env_mod_name(env, env_files):
        for e in env_files:
            e = e.replace('.py', '')
            if env.lower() == e.lower():
                return 'Fw.Env.{env}'.format(env=e)

        env_li = [e.replace('.py', '').lower() for e in env_files]
        raise ImportError('The indicated environment ("{env}") is not a valid environment. '
                          'Currently available environments are: "{envs}"'
                          .format(env=env.lower(),
                                  envs=", ".join(env_li)))

    @staticmethod
    def _get_env_files():
        env_dir = Path(*Path(sets.__file__).parts[:-1], 'Env')
        return [f for f in os.listdir(env_dir) if (f[0] != '_') and ('.py' in f)]

    @staticmethod
    def load_settings_file():
        set_dict = {s: getattr(sets, s) for s in dir(sets) if s[0] != '_'}
        return pd.Series(set_dict)

    def load_environment(self, env):
        if env is not None:
            env_files = self._get_env_files()
            env_mod_name = self._get_env_mod_name(env, env_files)
            mod = importlib.import_module(env_mod_name)
            env_dict = {s.upper(): getattr(mod, s) for s in dir(mod) if s[0] != '_'}
        else:
            env_dict = {}
        env_dict['ENV_NAME'] = env
        return pd.Series(env_dict)







