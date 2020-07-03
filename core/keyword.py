import os
import pathlib
import importlib
import inspect


class Keywords:
    def __init__(self, locations):
        self.locs = locations
        self._discover_keyword()

    def _discover_keyword(self):
        self.kws = {}
        for loc in self.locs:
            loc = pathlib.Path(loc)
            if pathlib.Path.is_file(loc):
                files = [loc]
            elif pathlib.Path.is_dir(loc):
                files = list()
                for path, subdirs, file_list in os.walk(loc):
                    for name in file_list:
                        files.append(pathlib.Path(path, name))
            else:
                continue
            for file in files:
                if file.parts[-1][-3:].upper() == '.PY':
                    keywords = self._get_keywords_from_file(file)
                    self.kws.update({k: kw for k, kw in keywords.items() if k[0] != '_'})

    def _get_keywords_from_file(self, file):
        keywords = {}
        spec = importlib.util.spec_from_file_location(str(file), pathlib.Path(file))
        file_mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(file_mod)
        except:
            return keywords
        classes = [m for m in inspect.getmembers(file_mod, inspect.isclass) if m[1].__module__ == str(file)]
        for c in classes:
            keywords.update({m[0]: m[1] for m in inspect.getmembers(c[1](), inspect.ismethod)})
        keywords.update({m[0]: m[1] for m in inspect.getmembers(file_mod,
                                                                inspect.isfunction) if m[1].__module__ == str(file)})
        return keywords

    def _get_variable_info(self, name: str):
        func = self.kws.get(name)
        all_vars = func.__code__.co_varnames
        defaults = func.__defaults__
        if defaults:
            mandatory = all_vars[:-len(defaults)]
            optional = {var: val for var, val in zip(all_vars[-len(defaults):], defaults)}
        else:
            mandatory = all_vars
            optional = {}
        return mandatory, optional

    def get_mandatory_fields(self, name: str):
        mandatory = self._get_variable_info(name)[0]
        return list(mandatory)

    def get_optional_fields(self, name: str):
        return self._get_variable_info(name)[1]

    def get_conditional_fields(self, name: str):
        return {}

    def get_all_keywords(self):
        return list(self.kws.keys())

