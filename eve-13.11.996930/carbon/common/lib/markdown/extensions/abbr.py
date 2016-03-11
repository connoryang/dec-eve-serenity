#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\abbr.py
import re
import markdown
from markdown.util import etree
ABBR_REF_RE = re.compile('[*]\\[(?P<abbr>[^\\]]*)\\][ ]?:\\s*(?P<title>.*)')

class AbbrExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('abbr', AbbrPreprocessor(md), '<reference')


class AbbrPreprocessor(markdown.preprocessors.Preprocessor):

    def run(self, lines):
        new_text = []
        for line in lines:
            m = ABBR_REF_RE.match(line)
            if m:
                abbr = m.group('abbr').strip()
                title = m.group('title').strip()
                self.markdown.inlinePatterns['abbr-%s' % abbr] = AbbrPattern(self._generate_pattern(abbr), title)
            else:
                new_text.append(line)

        return new_text

    def _generate_pattern(self, text):
        chars = list(text)
        for i in range(len(chars)):
            chars[i] = '[%s]' % chars[i]

        return '(?P<abbr>\\b%s\\b)' % ''.join(chars)


class AbbrPattern(markdown.inlinepatterns.Pattern):

    def __init__(self, pattern, title):
        markdown.inlinepatterns.Pattern.__init__(self, pattern)
        self.title = title

    def handleMatch(self, m):
        abbr = etree.Element('abbr')
        abbr.text = m.group('abbr')
        abbr.set('title', self.title)
        return abbr


def makeExtension(configs = None):
    return AbbrExtension(configs=configs)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
