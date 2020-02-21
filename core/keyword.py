from pathlib import Path
import importlib
import importlib.util
import os
import inspect

from fw.core.utilities import Util
from fw.core.conventions import KeywordNameConventions

import logging
import pandas as pd


class KeywordCoreLayer:
    @staticmethod
    def _get_files_from_dirs(kw_dirs, fname_fltr_func=lambda file: True):
        files = []
        for kw_dir in kw_dirs:
            all_files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(kw_dir)) for f in fn]
            test_files = [Path(f) for f in all_files if f[0] != '_' and f[-3:] == '.py' and fname_fltr_func(f)]
            if len(test_files) == 0:
                logging.debug('Directory "{}" does not contain a valid keyword files.'.format(kw_dir))
            else:
                files.extend(test_files)
        return files

    @staticmethod
    def _load_module_from_file(file, mod_name='temp_mod'):
        spec = importlib.util.spec_from_file_location(mod_name, file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _get_own_classes(self, file):
        mod = self._load_module_from_file(file, 'temp_mod')
        classes = []
        for name, obj in inspect.getmembers(mod):
            if inspect.isclass(obj) and 'temp_mod' in str(obj):
                classes.append(obj)
        return classes

    def _get_funcs(self, cls, return_name=True, name_fltr_func=None):
        cls_li = []
        funcs = []
        filtr_f =  name_fltr_func if name_fltr_func is not None else lambda n: True
        for name, obj in inspect.getmembers(cls):
            if inspect.isfunction(obj) and filtr_f(name) and name[0] != '_':
                cls_li.append(cls)
                if return_name:
                    funcs.append(name)
                else:
                    funcs.append(obj)
        return funcs, cls_li

    def _correct_to_path(self, kw_dirs):
        result = []
        for d in kw_dirs:
            assert '.py' != str(d)[-3:], 'Keyword directory "{}" is not a valid directory, but is a filename'.format(d)
            d_corr = Path(*str(d).split('.'))
            if str(self._fw_dir) not in str(d_corr):
                result.append(Path(self._fw_dir, d_corr))
            else:
                result.append(d_corr)
        return result


class KeywordSimplifiedLayer(KeywordCoreLayer):

    def _combine_to_class(self, methods, classes, class_type, name_func=None, **defaults):
        assert class_type in ['Data', 'Config', 'Keywords'], 'Class type {} is unsupported'.format(class_type)

        name_func = name_func if name_func is not None else lambda f: f.__name__

        class CarrierClass:
            pass

        for m, c in zip(methods, classes):
            new_name = name_func(m)
            if class_type == 'Data':
                setattr(CarrierClass, new_name, staticmethod(self._get_data_method(m, new_name)))
            elif class_type == 'Config':
                setattr(CarrierClass, new_name, staticmethod(self._get_config_method(m, new_name, **defaults)))
            else:
                setattr(CarrierClass, new_name, staticmethod(self._get_keyword_method(m, c, new_name)))

        return CarrierClass

    def _get_config_method(self, func, new_name=None, **defaults):
        if new_name is None:
            new_name = func.__name__
        man, opt = self._get_var_info(func)
        defaults['mandatory_variables'] = [m for m in man if m.lower() != 'self']
        defaults['optional_variables'] = opt

        def default_conf():
            return defaults

        default_conf.__name__ = new_name
        return default_conf

    def _get_data_method(self, func, new_name=None):
        if new_name is None:
            new_name = func.__name__
        man, opts = self._get_var_info(func)

        def default_data(fw):
            fw.DATA = fw.lib.safe_assign(fw.DATA,
                                         **opts)
            return fw

        default_data.__name__ = new_name
        return default_data

    def _get_keyword_method(self, func, cls, new_name):
        if new_name is None:
            new_name = func.__name__
        all = self._get_var_info(func, True)

        def default_keyword(fw):
            assert not isinstance(fw.DATA, pd.DataFrame), 'DataFrame iteration is only supported for Extended keywords'
            data = {k: fw.DATA.to_dict().get(k.upper()) for k in all if k.lower() != 'self'}
            if all[0].lower() == 'self':
                data[all[0]] = cls()
                return func(**data)
            else:
                return func(**data)

        default_keyword.__name__ = new_name
        default_keyword.__doc__ = func.__doc__
        return default_keyword

    @staticmethod
    def _get_var_info(func, return_all=False):
        varinfo = inspect.getfullargspec(func)
        all_vars = varinfo[0]
        if return_all:
            return all_vars
        defaults = varinfo[3]
        if defaults:
            mandatory = all_vars[:-len(defaults)]
            optional = {var: val for var, val in zip(all_vars[-len(defaults):], defaults)}
        else:
            mandatory = all_vars
            optional = {}
        return mandatory, optional


class ExtendedKeywords(KeywordCoreLayer):
    def __init__(self):
        self._fw_dir = Util().fw_dir()
        self._files = self._get_qualified_files()
        logging.debug('The following extended keyword modules are detected: "{}".'
                      .format('", "'.join(map(str, self._files))))

    def _get_qualified_files(self):
        kw_dirs_raw = Util().settings().EXTENDED_KW_DIRECTORY
        kw_dirs = self._correct_to_path(kw_dirs_raw)

        def func(f):
            return 'keywords.py' == f.lower()[-11:]

        return self._get_files_from_dirs(kw_dirs, func)

    def get_names(self):
        data = [x for x in self._get_funcs(self.get_class('Data'))[0]]
        conf = [x for x in self._get_funcs(self.get_class('Config'))[0]]
        keyw = [x for x in self._get_funcs(self.get_class('Keywords'))[0]]
        return tuple(set(data) & set(conf) & set(keyw))

    def get_class(self, method_type):
        cls_li = []
        for f in self._files:
            classes = self._get_own_classes(f)
            cls_li.extend([x for x in classes if x.__name__ == method_type])

        class Temp(*cls_li):
            pass

        Temp.__name__ = method_type
        return Temp


class SlimKeywords(KeywordSimplifiedLayer):
    def __init__(self):
        self._fw_dir = Util().fw_dir()
        self._files = self._get_qualified_files()
        self._default_props = Util().settings().SLIM_DEFAULT_KW_PROPERTIES
        logging.debug('The following slim keyword modules are detected: "{}".'
                      .format('", "'.join(map(str, self._files))))

    def _get_qualified_files(self):
        kw_dirs_raw = Util().settings().SLIM_KW_DIRECTORY
        kw_dirs = self._correct_to_path(kw_dirs_raw)
        return self._get_files_from_dirs(kw_dirs)

    def _get_kw_funcs(self):
        cls_li = []
        meths = []
        for f in self._files:
            classes = self._get_own_classes(f)
            for c in classes:
                ms, cls = self._get_funcs(c, False)
                meths.extend(ms)
                cls_li.extend(cls)
            mod = self._load_module_from_file(f)
            fs, mods = self._get_funcs(mod, False)
            meths.extend(fs)
            cls_li.extend(mods)
        return meths, cls_li

    def get_names(self):
        data = [x for x in self._get_funcs(self.get_class('Data'))[0]]
        conf = [x for x in self._get_funcs(self.get_class('Config'))[0]]
        keyw = [x for x in self._get_funcs(self.get_class('Keywords'))[0]]
        return tuple(set(data) & set(conf) & set(keyw))

    def get_class(self, method_type):
        funcs, classes = self._get_kw_funcs()
        return self._combine_to_class(funcs, classes, method_type, **self._default_props)


class PageObjectModelKeywords(KeywordSimplifiedLayer):
    def __init__(self):
        self._fw_dir = Util().fw_dir()
        self._files = self._get_qualified_files()
        self._default_props = Util().settings().POM_DEFAULT_KW_PROPERTIES
        logging.debug('The following pom keyword modules are detected: "{}".'
                      .format('", "'.join(map(str, self._files))))

    def _get_qualified_files(self):
        kw_dirs_raw = Util().settings().POM_DIRECTORY
        kw_dirs = self._correct_to_path(kw_dirs_raw)
        return self._get_files_from_dirs(kw_dirs)

    @staticmethod
    def _name_filter_func(name):
        result = False
        prefs = Util().settings().POM_VALID_PREFIXES
        for p in prefs:
            if p.lower() == name[0:len(p)].lower():
                result = True
        return result

    @staticmethod
    def _pom_rename_func(func):
        full_path = func.__fileloc__
        file_name = full_path.parts[-1]
        return KeywordNameConventions().make_method_name(screen=file_name[:-3],
                                                         action=func.__name__)

    def _get_kw_funcs(self):
        cls_li = []
        meths = []
        files = []
        for f in self._files:
            classes = self._get_own_classes(f)
            for c in classes:
                ms, cs = self._get_funcs(c, False, self._name_filter_func)
                meths.extend(ms)
                cls_li.extend(cs)
                files.extend([f for _ in ms])
            mod = self._load_module_from_file(f)
            fs, ms = self._get_funcs(mod, False, self._name_filter_func)
            meths.extend(fs)
            cls_li.extend(ms)
            files.extend([f for _ in fs])
        return meths, cls_li, files

    def get_names(self):
        data = [x for x in self._get_funcs(self.get_class('Data'))[0]]
        conf = [x for x in self._get_funcs(self.get_class('Config'))[0]]
        keyw = [x for x in self._get_funcs(self.get_class('Keywords'))[0]]
        return tuple(set(data) & set(conf) & set(keyw))

    def get_class(self, method_type):
        funcs, cls_li, files = self._get_kw_funcs()
        for i in range(len(funcs)):
            funcs[i].__fileloc__ = files[i]
        return self._combine_to_class(funcs, cls_li, method_type, self._pom_rename_func, **self._default_props)


class KeywordMethods(ExtendedKeywords().get_class('Keywords'),
                     SlimKeywords().get_class('Keywords'),
                     PageObjectModelKeywords().get_class('Keywords')):
    pass


class ConfigMethods(ExtendedKeywords().get_class('Config'),
                    SlimKeywords().get_class('Config'),
                    PageObjectModelKeywords().get_class('Config')):
    pass


class DataMethods(ExtendedKeywords().get_class('Data'),
                  SlimKeywords().get_class('Data'),
                  PageObjectModelKeywords().get_class('Data')):
    pass


class KeywordInfo:
    def __init__(self):
        self._req_props = Util().settings().REQUIRED_KW_PROPERTIES

    def get_qualified_keywords(self):
        all_kws = list(ExtendedKeywords().get_names())
        all_kws.extend(SlimKeywords().get_names())
        if Util().settings().INCLUDE_POM_AS_KEYWORDS:
            all_kws.extend(PageObjectModelKeywords().get_names())
        return tuple([kw for kw in all_kws if self._check_qualification(kw)])

    def _check_qualification(self, name):
        valid = True
        for req in self._req_props:
            if getattr(ConfigMethods(), name)().get(req, '{{IKW}}') == '{{IKW}}':
                valid = False
        return valid

    @staticmethod
    def get_keyword_arguments(name: str, robot_mode=True):
        man_vars = getattr(ConfigMethods(), name)().get('mandatory_variables')
        opt_vars = getattr(ConfigMethods(), name)().get('optional_variables')
        if robot_mode:
            all_vars = ['{}=()'.format(var) for var in man_vars]
            if opt_vars is not None:
                all_vars.extend(['{}={}'.format(var, val) for var, val in opt_vars.items()])
        else:
            all_vars = list(man_vars)
            if opt_vars is not None:
                all_vars.extend(opt_vars)
        return all_vars

    @staticmethod
    def get_keyword_documentation(name: str):
        if name in dir(KeywordMethods()):
            return str(getattr(KeywordMethods(), name).__doc__)

    @staticmethod
    def get_mandatory_arguments(name: str):
        return [v.upper() for v in getattr(ConfigMethods(), name)().get('mandatory_variables')]

    @staticmethod
    def get_optional_arguments(name: str):
        return [v.upper() for v in getattr(ConfigMethods(), name)().get('optional_variables')]