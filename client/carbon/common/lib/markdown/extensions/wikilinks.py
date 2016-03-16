#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\wikilinks.py
import markdown
import re

def build_url(label, base, end):
    clean_label = re.sub('([ ]+_)|(_[ ]+)|([ ]+)', '_', label)
    return '%s%s%s' % (base, clean_label, end)


class WikiLinkExtension(markdown.Extension):

    def __init__(self, configs):
        self.config = {'base_url': ['/', 'String to append to beginning or URL.'],
         'end_url': ['/', 'String to append to end of URL.'],
         'html_class': ['wikilink', 'CSS hook. Leave blank for none.'],
         'build_url': [build_url, 'Callable formats URL from label.']}
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        self.md = md
        WIKILINK_RE = '\\[\\[([\\w0-9_ -]+)\\]\\]'
        wikilinkPattern = WikiLinks(WIKILINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.add('wikilink', wikilinkPattern, '<not_strong')


class WikiLinks(markdown.inlinepatterns.Pattern):

    def __init__(self, pattern, config):
        markdown.inlinepatterns.Pattern.__init__(self, pattern)
        self.config = config

    def handleMatch(self, m):
        if m.group(2).strip():
            base_url, end_url, html_class = self._getMeta()
            label = m.group(2).strip()
            url = self.config['build_url'](label, base_url, end_url)
            a = markdown.util.etree.Element('a')
            a.text = label
            a.set('href', url)
            if html_class:
                a.set('class', html_class)
        else:
            a = ''
        return a

    def _getMeta(self):
        base_url = self.config['base_url']
        end_url = self.config['end_url']
        html_class = self.config['html_class']
        if hasattr(self.md, 'Meta'):
            if self.md.Meta.has_key('wiki_base_url'):
                base_url = self.md.Meta['wiki_base_url'][0]
            if self.md.Meta.has_key('wiki_end_url'):
                end_url = self.md.Meta['wiki_end_url'][0]
            if self.md.Meta.has_key('wiki_html_class'):
                html_class = self.md.Meta['wiki_html_class'][0]
        return (base_url, end_url, html_class)


def makeExtension(configs = None):
    return WikiLinkExtension(configs=configs)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
