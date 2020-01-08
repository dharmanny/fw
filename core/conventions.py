import fw.settings as sets
import re


class KeywordNameConventions:
    @staticmethod
    def validate_pom_default_name():
        name = sets.POM_KW_NAMING_CONVENTION.format(screen='a', action='b')
        invalids = []
        for char in name:
            if re.search('\w|(|)|[ ]', char) is None:
                invalids.append(char)
        if len(invalids) != 0:
            raise NameError('The given pom naming convention is invalid. It contains non-supported characters ("{}"). '
                            'The name is given in the settings via the POM_KW_NAMING_CONVENTION parameter.'
                            .format('", "'.join(invalids)))

    def make_method_name(self, **variables):
        name = sets.POM_KW_NAMING_CONVENTION.format(**variables)
        for kw_char, m_char in self.mapper.items():
            name = name.replace(kw_char, m_char)
        return name

    def make_keyword_name(self, **variables):
        name = sets.POM_KW_NAMING_CONVENTION.format(**variables)
        for kw_char, m_char in self.mapper.items():
            name = name.replace(m_char, kw_char)
        return name

    def convert_name(self, name: str, in_name='method'):
        if in_name.lower() == 'method':
            for kw_char, m_char in self.mapper.items():
                name = name.replace(m_char, kw_char)
        elif in_name.lower() == 'keyword':
            for kw_char, m_char in self.mapper.items():
                name = name.replace(m_char, kw_char)
        else:
            raise ValueError('The indicated name is not a valid option.')
        return name

    mapper = {r'(': '_BO_',
              r')': '_BC_',
              r' ': '_'}
