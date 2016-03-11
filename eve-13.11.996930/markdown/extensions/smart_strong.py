#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\smart_strong.py
import re
import markdown
from markdown.inlinepatterns import SimpleTagPattern
SMART_STRONG_RE = '(?<!\\w)(_{2})(?!_)(.+?)(?<!_)\\2(?!\\w)'
STRONG_RE = '(\\*{2})(.+?)\\2'

class SmartEmphasisExtension(markdown.extensions.Extension):

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['strong'] = SimpleTagPattern(STRONG_RE, 'strong')
        md.inlinePatterns.add('strong2', SimpleTagPattern(SMART_STRONG_RE, 'strong'), '>emphasis2')


def makeExtension(configs = {}):
    return SmartEmphasisExtension(configs=dict(configs))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
