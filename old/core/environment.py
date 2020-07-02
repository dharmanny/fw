from pathlib import Path
import os
import fw
import importlib
import pandas as pd


class Env:
    def __init__(self):
        self._env_li = self.get_full_env_mods()

    def load_environment_settings(self, env):
        env_dict = {}
        if env is not None:
            if isinstance(env, str):
                env = (env,)
            else:
                env = tuple(map(str, env))
            for env_part in env:
                env_part_tuple = env[:env.index(env_part)+1]
                mod_name = 'fw.env.{}'.format('.'.join(env_part_tuple))
                try:
                    mod = importlib.import_module(mod_name)
                except ModuleNotFoundError:
                    raise ImportError('The indicated environment ({env}) was not defined. '
                                      'Add the environment to the fw/env folder.'.format(env='/'.join(env)))
                new_dict = {s.upper(): getattr(mod, s) for s in dir(mod) if s[0] != '_'}
                env_dict.update(new_dict)
        else:
            env_dict = {}
        env_dict['ENV_NAME'] = env
        return pd.Series(env_dict)

    def _make_tree(self, direct, flat=True):
        dir_cont = [f for f in os.listdir(direct) if f[:1] != '_']
        dir_cont.extend([f for f in os.listdir(direct) if f == '__init__.py'])
        cont = []
        if '__init__.py' not in dir_cont:
            open(Path(direct, '__init__.py'), 'w+').close()
            importlib.reload(fw)
        for f in dir_cont:
            full_path = Path(direct, f)
            if os.path.isdir(full_path):
                result = ['{}.{}'.format(f, r) for r in self._make_tree(full_path, flat)]
                cont.extend(result)
            elif f[-3:].lower() == '.py':
                if f[:-3] not in dir_cont:
                    cont.append(f[:-3])
        return cont

    def get_full_env_mods(self):
        direct = Path(fw.old.core.utilities.Util().fw_dir(), 'env')
        flat_tree = self._make_tree(direct, True)
        return tuple(flat_tree)
