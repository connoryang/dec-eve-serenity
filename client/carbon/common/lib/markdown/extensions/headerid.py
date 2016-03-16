#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\headerid.py
import markdown
from markdown.util import etree
import re
from string import ascii_lowercase, digits, punctuation
import logging
import unicodedata
logger = logging.getLogger('MARKDOWN')
IDCOUNT_RE = re.compile('^(.*)_([0-9]+)$')

def slugify(value, separator):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = re.sub('[^\\w\\s-]', '', value.decode('ascii')).strip().lower()
    return re.sub('[%s\\s]+' % separator, separator, value)


def unique(id, ids):
    while id in ids or not id:
        m = IDCOUNT_RE.match(id)
        if m:
            id = '%s_%d' % (m.group(1), int(m.group(2)) + 1)
        else:
            id = '%s_%d' % (id, 1)

    ids.append(id)
    return id


def itertext(elem):
    if elem.text:
        yield elem.text
    for e in elem:
        for s in itertext(e):
            yield s

        if e.tail:
            yield e.tail


class HeaderIdTreeprocessor(markdown.treeprocessors.Treeprocessor):
    IDs = set()

    def run(self, doc):
        start_level, force_id = self._get_meta()
        slugify = self.config['slugify']
        sep = self.config['separator']
        for elem in doc.getiterator():
            if elem.tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                if force_id:
                    if 'id' in elem.attrib:
                        id = elem.id
                    else:
                        id = slugify(u''.join(itertext(elem)), sep)
                    elem.set('id', unique(id, self.IDs))
                if start_level:
                    level = int(elem.tag[-1]) + start_level
                    if level > 6:
                        level = 6
                    elem.tag = 'h%d' % level

    def _get_meta(self):
        level = int(self.config['level']) - 1
        force = self._str2bool(self.config['forceid'])
        if hasattr(self.md, 'Meta'):
            if self.md.Meta.has_key('header_level'):
                level = int(self.md.Meta['header_level'][0]) - 1
            if self.md.Meta.has_key('header_forceid'):
                force = self._str2bool(self.md.Meta['header_forceid'][0])
        return (level, force)

    def _str2bool(self, s, default = False):
        s = str(s)
        if s.lower() in ('0', 'f', 'false', 'off', 'no', 'n'):
            return False
        if s.lower() in ('1', 't', 'true', 'on', 'yes', 'y'):
            return True
        return default


class HeaderIdExtension(markdown.Extension):

    def __init__(self, configs):
        self.config = {'level': ['1', 'Base level for headers.'],
         'forceid': ['True', 'Force all headers to have an id.'],
         'separator': ['-', 'Word separator.'],
         'slugify': [slugify, 'Callable to generate anchors']}
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        self.processor = HeaderIdTreeprocessor()
        self.processor.md = md
        self.processor.config = self.getConfigs()
        md.treeprocessors.add('headerid', self.processor, '>inline')

    def reset(self):
        self.processor.IDs = []


def makeExtension(configs = None):
    return HeaderIdExtension(configs=configs)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
