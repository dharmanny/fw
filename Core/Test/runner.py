import importlib
import os
import unittest as ut
from pathlib import Path

suite_dir = Path(*Path(__file__).parts[:-1], 'suites')
test_modules = []
for f in os.listdir(suite_dir):
    if (f[0] != '_') and ('.py' in f):
        base_name = f.replace('.py', '')
        mod_name = 'fw.core.test.suites.{suite}'.format(suite=base_name)
        mod = importlib.import_module(mod_name)
        names = [x for x in mod.__dict__ if not x.startswith("_")]
        globals().update({k: getattr(mod, k) for k in names})
if __name__ == '__main__':
    ut.main()


