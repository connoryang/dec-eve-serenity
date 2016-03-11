#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\config.py
import os, re, sys
from coverage.backward import string_class, iitems
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

class HandyConfigParser(configparser.RawConfigParser):

    def read(self, filename):
        kwargs = {}
        if sys.version_info >= (3, 2):
            kwargs['encoding'] = 'utf-8'
        return configparser.RawConfigParser.read(self, filename, **kwargs)

    def get(self, *args, **kwargs):
        v = configparser.RawConfigParser.get(self, *args, **kwargs)

        def dollar_replace(m):
            word = [ w for w in m.groups() if w is not None ][0]
            if word == '$':
                return '$'
            else:
                return os.environ.get(word, '')

        dollar_pattern = '(?x)   # Use extended regex syntax\n            \\$(?:                   # A dollar sign, then\n            (?P<v1>\\w+) |           #   a plain word,\n            {(?P<v2>\\w+)} |         #   or a {-wrapped word,\n            (?P<char>[$])           #   or a dollar sign.\n            )\n            '
        v = re.sub(dollar_pattern, dollar_replace, v)
        return v

    def getlist(self, section, option):
        value_list = self.get(section, option)
        values = []
        for value_line in value_list.split('\n'):
            for value in value_line.split(','):
                value = value.strip()
                if value:
                    values.append(value)

        return values

    def getlinelist(self, section, option):
        value_list = self.get(section, option)
        return list(filter(None, value_list.split('\n')))


DEFAULT_EXCLUDE = ['(?i)# *pragma[: ]*no *cover']
DEFAULT_PARTIAL = ['(?i)# *pragma[: ]*no *branch']
DEFAULT_PARTIAL_ALWAYS = ['while (True|1|False|0):', 'if (True|1|False|0):']

class CoverageConfig(object):

    def __init__(self):
        self.attempted_config_files = []
        self.config_files = []
        self.branch = False
        self.cover_pylib = False
        self.data_file = '.coverage'
        self.parallel = False
        self.timid = False
        self.source = None
        self.debug = []
        self.exclude_list = DEFAULT_EXCLUDE[:]
        self.ignore_errors = False
        self.include = None
        self.omit = None
        self.partial_list = DEFAULT_PARTIAL[:]
        self.partial_always_list = DEFAULT_PARTIAL_ALWAYS[:]
        self.precision = 0
        self.show_missing = False
        self.html_dir = 'htmlcov'
        self.extra_css = None
        self.html_title = 'Coverage report'
        self.xml_output = 'coverage.xml'
        self.paths = {}

    def from_environment(self, env_var):
        env = os.environ.get(env_var, '')
        if env:
            self.timid = '--timid' in env

    MUST_BE_LIST = ['omit', 'include', 'debug']

    def from_args(self, **kwargs):
        for k, v in iitems(kwargs):
            if v is not None:
                if k in self.MUST_BE_LIST and isinstance(v, string_class):
                    v = [v]
                setattr(self, k, v)

    def from_file(self, filename):
        self.attempted_config_files.append(filename)
        cp = HandyConfigParser()
        files_read = cp.read(filename)
        if files_read is not None:
            self.config_files.extend(files_read)
        for option_spec in self.CONFIG_FILE_OPTIONS:
            self.set_attr_from_config_option(cp, *option_spec)

        if cp.has_section('paths'):
            for option in cp.options('paths'):
                self.paths[option] = cp.getlist('paths', option)

    CONFIG_FILE_OPTIONS = [('branch', 'run:branch', 'boolean'),
     ('cover_pylib', 'run:cover_pylib', 'boolean'),
     ('data_file', 'run:data_file'),
     ('debug', 'run:debug', 'list'),
     ('include', 'run:include', 'list'),
     ('omit', 'run:omit', 'list'),
     ('parallel', 'run:parallel', 'boolean'),
     ('source', 'run:source', 'list'),
     ('timid', 'run:timid', 'boolean'),
     ('exclude_list', 'report:exclude_lines', 'linelist'),
     ('ignore_errors', 'report:ignore_errors', 'boolean'),
     ('include', 'report:include', 'list'),
     ('omit', 'report:omit', 'list'),
     ('partial_list', 'report:partial_branches', 'linelist'),
     ('partial_always_list', 'report:partial_branches_always', 'linelist'),
     ('precision', 'report:precision', 'int'),
     ('show_missing', 'report:show_missing', 'boolean'),
     ('html_dir', 'html:directory'),
     ('extra_css', 'html:extra_css'),
     ('html_title', 'html:title'),
     ('xml_output', 'xml:output')]

    def set_attr_from_config_option(self, cp, attr, where, type_ = ''):
        section, option = where.split(':')
        if cp.has_option(section, option):
            method = getattr(cp, 'get' + type_)
            setattr(self, attr, method(section, option))
