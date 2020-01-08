# Specifying data
CSV_SEP = ";"
NA_FILL = ""
EVAL_INDICATOR = 'ev:'


""" The following section of settings cannot be changed on initiating the framework, 
and thus can only be changed by altering this file. """

# About keywords
KW_DIRECTORY = ('keywords',)
REQUIRED_KW_PROPERTIES = ('mandatory_variables', 'iterable',)

# Pom descriptors
POM_MODULES = ('system.pom',)
POM_KW_NAMING_CONVENTION = '({screen}) {action}'
POM_VALID_PREFIXES = ('get', 'assert', 'click', 'input', 'select')
POM_DEFAULT_KW_PROPERTIES = {'iterable': None}


LIBRARY_MODULES = ('lib',)