from pathlib import Path
import importlib
import os
import re
import inspect

from fw.core.utilities import Util
from fw.core.conventions import KeywordNameConventions

import logging
import pandas as pd


class ExtendedKeywords:
    def __init__(self):
        self._fw_dir = Path(*Path(__file__).parts[:-2])
        self._kw_dirs = [Path(self._fw_dir, d) for d in Util().settings().EXTENDED_KW_DIRECTORY]
        self._kw_files, self.mods = self._get_kw_files_and_mods()
        logging.debug('The following extended keyword modules are detected: "{}".'.format('", "'.join(self.mods)))

    def _get_kw_files_and_mods(self):
        files = []
        mods = []
        for kw_dir in self._kw_dirs:
            for d in os.listdir(kw_dir):
                base_dir = Path(kw_dir, d)
                if 'keywords.py' in os.listdir(base_dir):
                    files.append(Path(base_dir, 'keywords.py'))
                    base_mod = '.'.join(base_dir.parts[base_dir.parts.index('fw'):])
                    mods.append('{base_mod}.keywords'.format(base_mod=base_mod))
                else:
                    logging.debug('Directory "{}" does not contain a keywords.py file.'.format(d))
        return files, mods

    @staticmethod
    def _get_kw_attributes(cls):
        kws = []
        for met in dir(cls):
            attr = getattr(cls, met)
            if callable(attr) and met[0] != '_':
                kws.append(met)
        if len(kws) == 0:
            logging.debug('No methods were added from class "{}".'.format(str(cls)))
        else:
            logging.debug('The following methods are taken from class "{cls}": "{mtds}"'
                          .format(cls=str(cls), mtds='","'.join(kws)))
        return kws

    @staticmethod
    def _get_class_attr(mod, cls):
        try:
            return getattr(importlib.import_module(mod), cls)
        except AttributeError:
            return None

    def get_all_names(self):
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


class PageObjectModelKeywords:
    def __init__(self):
        self._fw_dir = Path(*Path(__file__).parts[:-2])
        self.mods = self._get_all_modules()
        KeywordNameConventions.validate_pom_default_name()

    def _get_all_modules(self):
        all_mods = []
        for p in Util().settings().POM_MODULES:
            folder_li = [p for p in re.split(r'[.]|/|\\', p) if p != 'fw']
            folder_path = Path(self._fw_dir, *folder_li)
            mods = [f[:-3] for f in os.listdir(folder_path) if f[0] != '_' and f[-3:] == '.py']
            all_mods.extend(['fw.{fold}.{mod}'.format(fold='.'.join(folder_li), mod=m) for m in mods])
        return all_mods

    @staticmethod
    def _decorate_with_new_name(func, screen, cls=None, kw_name=False):
        if kw_name:
            new_name = KeywordNameConventions().make_keyword_name(screen=screen, action=func.__name__)
        else:
            new_name = KeywordNameConventions().make_method_name(screen=screen, action=func.__name__)

        def new_func(*args, **kwargs):
            if cls is not None:
                return func(cls(), *args, **kwargs)
            else:
                return func(*args, **kwargs)
        new_func.__name__ = new_name
        new_func.__doc__ = func.__doc__
        return new_func

    @staticmethod
    def _get_own_classes(mod_name):
        mod = importlib.import_module(mod_name)
        classes = []
        for c_name in dir(mod):
            if c_name[0:1] != '_':
                c = getattr(mod, c_name)
                if inspect.isclass(c):
                    if mod_name in str(c):
                        classes.append(c)
        return classes

    @staticmethod
    def _validate_pom_prefix(name: str):
        result = False
        for pref in Util().settings().POM_VALID_PREFIXES:
            if name[0:len(pref)] == pref:
                result = True
        return result

    def _validate_attribute(self, attr):
        if callable(attr) and hasattr(attr, '__name__'):
            name = attr.__name__
            if self._validate_pom_prefix(name) and name[:1] != '_':
                return attr

    @staticmethod
    def _get_var_info(func):
        all_vars = func.__code__.co_varnames[1:]
        defaults = func.__defaults__
        if defaults:
            mandatory = all_vars[:-len(defaults)]
            optional = {var: val for var, val in zip(all_vars[-len(defaults):], defaults)}
        else:
            mandatory = all_vars
            optional = {}
        return mandatory, optional

    def _create_data_methods(self, cls, screen):
        methods = []
        for attr_name in dir(cls):
            func = self._validate_attribute(getattr(cls, attr_name))
            if func:
                man, opt = self._get_var_info(func)
                opt = {var.upper(): val for var, val in opt.items()}
                def default_data(fwo):
                    fwo.DATA = fwo.lib.safe_assign(fwo.DATA, **opt)
                default_data.__name__ = func.__name__
                methods.append(self._decorate_with_new_name(default_data, screen))
        return methods

    def _create_config_methods(self, cls, screen):
        methods = []
        for attr_name in dir(cls):
            func = self._validate_attribute(getattr(cls, attr_name))
            if func:
                var_reqs = ('mandatory_variables', 'optional_variables')
                mapping = {r: v for r, v in zip(var_reqs, self._get_var_info(func))}
                for req in Util().settings().REQUIRED_KW_PROPERTIES:
                    if req.lower() not in var_reqs:
                        mapping[req] = Util().settings().POM_DEFAULT_KW_PROPERTIES.get(req)

                def default_config():
                    return mapping
                default_config.__name__ = func.__name__
                methods.append(self._decorate_with_new_name(default_config, screen, kw_name=True))
        return methods

    @staticmethod
    def _extract_relevant_vars(all_vars, mapper):
        print(mapper)
        mapper = {k.upper(): v for k, v in mapper.items()}
        new_dict = {}
        for var in all_vars:
            new_dict[var] = mapper.get(var.upper())
        return new_dict

    def _get_kw_wrapper_func(self, func):
        man, opt = self._get_var_info(func)
        all_vars = list(man)
        all_vars.extend(opt.keys())

        def default_kw(own_cls, *args):
            data = args[0].DATA
            if data is None:
                kwargs = {}
            elif isinstance(data, pd.DataFrame):
                logging.info('When a pom object is executed, it only accepts rows, but a DataFrame was passe.'
                             'The first row of the DataFrame will be executed only.')
                kwargs = data.iloc[0].to_dict()
            elif isinstance(data, pd.Series):
                kwargs = data.to_dict()
            else:
                raise TypeError('Data was of unsupported type: "{}".'.format(data.__class__))
            kwargs = self._extract_relevant_vars(all_vars, kwargs)
            return func(own_cls, **kwargs)

        default_kw.__name__ = func.__name__
        default_kw.__doc__ = func.__doc__
        return default_kw

    def _create_kw_methods(self, cls, screen, kw_mode=True):
        methods = []
        for attr_name in dir(cls):
            func = self._validate_attribute(getattr(cls, attr_name))
            if func:
                if kw_mode:
                    new_func = self._get_kw_wrapper_func(func)
                    methods.append(self._decorate_with_new_name(new_func, screen, cls))
                else:
                    methods.append(self._decorate_with_new_name(func, screen, cls))
        return methods

    def _get_name_per_module(self, cls, screen, kw_mode=True):
        names = []
        for attr_name in dir(cls):
            func = self._validate_attribute(getattr(cls, attr_name))
            if func:
                if kw_mode:
                    names.append(KeywordNameConventions().make_keyword_name(screen=screen, action=attr_name))
                else:
                    names.append(KeywordNameConventions().make_method_name(screen=screen, action=attr_name))
        return names

    def get_all_names(self):
        names = []
        for mod_name in self.mods:
            classes = self._get_own_classes(mod_name)
            for cls in classes:
                screen = mod_name.split('.')[-1]
                names.extend(self._get_name_per_module(cls, screen, kw_mode=True))
        return names

    def get_keyword_classes(self, kw_mode=True):
        class PomKeywords:
            pass
        pom_methods = []
        for mod_name in self.mods:
            classes = self._get_own_classes(mod_name)
            for cls in classes:
                screen = mod_name.split('.')[-1]
                pom_methods.extend(self._create_kw_methods(cls, screen, kw_mode=kw_mode))
        for pm in pom_methods:
            setattr(PomKeywords, pm.__name__, staticmethod(pm))
        return PomKeywords

    def get_config_classes(self):
        class PomConfigs:
            pass
        pom_methods = []
        for mod_name in self.mods:
            classes = self._get_own_classes(mod_name)
            for cls in classes:
                screen = mod_name.split('.')[-1]
                pom_methods.extend(self._create_config_methods(cls, screen))
        for pm in pom_methods:
            setattr(PomConfigs, pm.__name__, staticmethod(pm))
        return PomConfigs

    def get_data_classes(self):
        class PomConfigs:
            pass
        pom_methods = []
        for mod_name in self.mods:
            classes = self._get_own_classes(mod_name)
            for cls in classes:
                screen = mod_name.split('.')[-1]
                pom_methods.extend(self._create_data_methods(cls, screen))
        for pm in pom_methods:
            setattr(PomConfigs, pm.__name__, staticmethod(pm))
        return PomConfigs

    def get_pom_as_system_interacts(self):
        return self.get_keyword_classes(kw_mode=False)


class KeywordMethods(*ExtendedKeywords().get_keyword_classes(),
                     PageObjectModelKeywords().get_keyword_classes()):
    pass


class ConfigMethods(*ExtendedKeywords().get_config_classes(),
                    PageObjectModelKeywords().get_config_classes()):
    pass


class DataMethods(*ExtendedKeywords().get_data_classes(),
                  PageObjectModelKeywords().get_data_classes()):
    pass


class KeywordInfo:
    @staticmethod
    def get_qualified_keywords():
        names = ExtendedKeywords().get_all_names()
        if Util().settings().INCLUDE_POM_AS_KEYWORDS:
            names.extend(PageObjectModelKeywords().get_all_names())
        req_props = Util().settings().REQUIRED_KW_PROPERTIES
        qualified_kws = []
        for name in names:
            valid = True
            for req in req_props:
                if getattr(ConfigMethods(), name)().get(req, '{{IKW}}') == '{{IKW}}':
                    valid = False
            if valid:
                qualified_kws.append(name)
        return qualified_kws

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
        new_name = KeywordNameConventions().convert_name(name, in_name='keyword').replace(' ', '_')
        if new_name in dir(KeywordMethods()):
            return str(getattr(KeywordMethods(), new_name).__doc__)

    @staticmethod
    def get_mandatory_arguments(name: str):
        return [v.upper() for v in getattr(ConfigMethods(), name)().get('mandatory_variables')]

    @staticmethod
    def get_optional_arguments(name: str):
        return [v.upper() for v in getattr(ConfigMethods(), name)().get('optional_variables')]