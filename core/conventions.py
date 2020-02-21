from fw.core.utilities import Util
from datetime import datetime
import re
import logging

class KeywordNameConventions:
    @staticmethod
    def validate_pom_default_name():
        name = Util().settings().POM_KW_NAMING_CONVENTION.format(screen='a', action='b')
        logging.debug('Resolved example name is: {}'.format(name))
        invalids = []
        for char in name:
            if re.search('\w|(|)|[ ]', char) is None:
                invalids.append(char)
        if len(invalids) != 0:
            raise NameError('The given pom naming convention is invalid. It contains non-supported characters ("{}"). '
                            'The name is given in the settings via the POM_KW_NAMING_CONVENTION parameter.'
                            .format('", "'.join(invalids)))

    def make_method_name(self, **variables):
        name = Util().settings().POM_KW_NAMING_CONVENTION.format(**variables)
        logging.debug('Resolved default name is: {}'.format(name))
        for kw_char, m_char in self.mapper.items():
            name = name.replace(kw_char, m_char)
            logging.debug('Resolved method name is: {}'.format(name))
        return name

    def make_keyword_name(self, **variables):
        name = Util().settings().POM_KW_NAMING_CONVENTION.format(**variables)
        logging.debug('Resolved default name is: {}'.format(name))
        for kw_char, m_char in self.mapper.items():
            name = name.replace(m_char, kw_char)
            logging.debug('Resolved keyword name is: {}'.format(name))
        return name

    def convert_name(self, name: str, in_name='method'):
        if in_name.lower() == 'method':
            for kw_char, m_char in self.mapper.items():
                name = name.replace(m_char, kw_char)
        elif in_name.lower() == 'keyword':
            for kw_char, m_char in self.mapper.items():
                name = name.replace(kw_char, m_char)
        else:
            raise ValueError('The indicated input name ({}) is not a valid option.'.format(in_name))
        return name

    mapper = {r'(': 'BO_',
              r')': 'BC_',
              r'_': '_'}


class FileName:
    def __init__(self, name_template=None):
        self.name_templ = Util().settings().DEFAULT_FILE_NAME if name_template is None else name_template

    @staticmethod
    def _get_default_parts():
        date = Util().settings().DEFAULT_DATE_FORMAT
        time = Util().settings().DEFAULT_TIME_FORMAT
        date_time = Util().settings().DEFAULT_DATETIME_FORMAT

        now = datetime.now()
        return {'datetime': now.strftime(date_time),
                'date': now.strftime(date),
                'time': now.strftime(time)}

    def get_filename(self, **kwargs):
        file_name = self.name_templ
        file_args = re.findall('\{(.*?)\}', file_name)
        defaults = {arg: '' for arg in file_args}
        defaults.update(self._get_default_parts())
        defaults.update(kwargs)
        new_name = file_name.format(**defaults)
        assert '' not in new_name.split('.'), 'The resulting filename - "{}" - is invalid.'.format(new_name)
        return new_name