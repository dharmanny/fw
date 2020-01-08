from pathlib import Path
import importlib
import os
import re
import inspect
import fw.settings as sets
from fw.core.conventions import KeywordNameConventions


class KeywordFiles:
    def __init__(self):
        self._fw_dir = Path(*Path(__file__).parts[:-2])
        self._kw_dirs = [Path(self._fw_dir, d) for d in sets.KW_DIRECTORY]
        self._kw_files, self.mods = self._get_kw_files_and_mods()
        self._kw_names = self._get_all_names()

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
        return files, mods

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


class PageObjectModelFiles:
    def __init__(self):
        self._fw_dir = Path(*Path(__file__).parts[:-2])
        self.mods = self._get_all_modules()
        KeywordNameConventions.validate_pom_default_name()

    def _get_all_modules(self):
        all_mods = []
        for p in sets.POM_MODULES:
            folder_li = [p for p in re.split(r'[.]|/|\\', p) if p != 'fw']
            folder_path = Path(self._fw_dir, *folder_li)
            mods = [f[:-3] for f in os.listdir(folder_path) if f[0] != '_' and f[-3:] == '.py']
            all_mods.extend(['fw.{fold}.{mod}'.format(fold='.'.join(folder_li), mod=m) for m in mods])
        return all_mods

    @staticmethod
    def _decorate_with_new_name(func, screen, cls=None):
        new_name = KeywordNameConventions().make_method_name(screen=screen, action=func.__name__)

        def new_func(*args, **kwargs):
            if cls is not None:
                return func(cls(), *args, **kwargs)
            else:
                return func(*args, **kwargs)
        new_func.__name__ = new_name
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
        for pref in sets.POM_VALID_PREFIXES:
            if name[0:len(pref)] == pref:
                result = True
        return result

    def _validate_attribute(self, attr):
        if callable(attr) and hasattr(attr, '__name__'):
            name = attr.__name__
            if self._validate_pom_prefix(name) and name[:1] != '_':
                return attr

    def _get_var_info(self, func):
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
                for req in sets.REQUIRED_KW_PROPERTIES:
                    if req.lower() not in var_reqs:
                        mapping[req] = sets.POM_DEFAULT_KW_PROPERTIES.get(req)

                def default_config():
                    return mapping
                default_config.__name__ = func.__name__
                methods.append(self._decorate_with_new_name(default_config, screen))
        return methods

    def _create_kw_methods(self, cls, screen, kw_mode=True):
        methods = []
        for attr_name in dir(cls):
            func = self._validate_attribute(getattr(cls, attr_name))
            if func:
                if kw_mode:
                    man, opt = self._get_var_info(func)
                    all_vars = list(man)
                    all_vars.extend(opt.keys())
                    def default_kw(own_cls, *args):
                        kwargs = args[0].DATA.filter(all_vars).to_dict()
                        return func(own_cls(), **kwargs)
                    default_kw.__name__ = func.__name__
                    methods.append(self._decorate_with_new_name(default_kw, screen, cls))
                else:
                    methods.append(self._decorate_with_new_name(func, screen, cls))
        return methods

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


class KeywordMethods(*KeywordFiles().get_keyword_classes(),
                     PageObjectModelFiles().get_keyword_classes()):
    pass
#
#
# class ConfigMethods(*KeywordFiles().get_config_classes(),
#                     *PageObjectModelFiles().get_config_classes()):
#     pass
#
#
# class DataMethods(*KeywordFiles().get_data_classes(),
#                   *PageObjectModelFiles().get_data_classes()):
#     pass
#
#
# class KeywordArgs(KeywordFiles):
#     def get_mandatory_args(self, name):
#         if name not in self.kw_names:
#             raise AssertionError('The indicated keyword ("{kw}") does not exist.'.format(kw=name))
#         try:
#             d = getattr(ConfigMethods(), name)
#         except AttributeError:
#             return []
#         return d.get('mandatory_variables', [])
#
#
# class KeywordQualification(KeywordFiles):
#     def get_qualified_keywords(self):
#         return self.kw_names

