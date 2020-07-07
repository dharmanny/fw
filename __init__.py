import fw.core.keyword as kw
import fw.core.settings as sets
import fw.core.data as dat
import fw.core.execution as exe

class fw:
    def __init__(self, env=None, **settings):
        sets.update_settings(**settings)
        self.keywords = kw.Keywords()

    def get_keyword_names(self):
        return self.keywords.get_all_keywords()

    def get_keyword_arguments(self, name: str):
        man = self.keywords.get_mandatory_fields(name)
        opt = self.keywords.get_optional_fields(name)
        man.extend(['{}={}'.format(k, v) for k, v in opt.items()])
        return man

    def get_keyword_documentation(self, name: str):
        return ''

    def run_keyword(self, name: str, args: list, kwargs: dict):
        data = dat.DataLoader(self.keywords).get_data(name, *args, **kwargs)
        dat.validate_data(data,
                          mandatory=self.keywords.get_mandatory_fields(name),
                          conditional=self.keywords.get_conditional_fields(name))
        data = self.keywords.return_data_case_sensitive(name, data)
        exe.Executer(keyword=self.keywords.kws.get(name),
                     data=data).run()

