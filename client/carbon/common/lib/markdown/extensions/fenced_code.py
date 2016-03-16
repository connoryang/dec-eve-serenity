#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\fenced_code.py
import re
import markdown
from markdown.extensions.codehilite import CodeHilite, CodeHiliteExtension
FENCED_BLOCK_RE = re.compile('(?P<fence>^(?:~{3,}|`{3,}))[ ]*(\\{?\\.?(?P<lang>[a-zA-Z0-9_+-]*)\\}?)?[ ]*\\n(?P<code>.*?)(?<=\\n)(?P=fence)[ ]*$', re.MULTILINE | re.DOTALL)
CODE_WRAP = '<pre><code%s>%s</code></pre>'
LANG_TAG = ' class="%s"'

class FencedCodeExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.add('fenced_code_block', FencedBlockPreprocessor(md), '_begin')


class FencedBlockPreprocessor(markdown.preprocessors.Preprocessor):

    def __init__(self, md):
        markdown.preprocessors.Preprocessor.__init__(self, md)
        self.checked_for_codehilite = False
        self.codehilite_conf = {}

    def run(self, lines):
        if not self.checked_for_codehilite:
            for ext in self.markdown.registeredExtensions:
                if isinstance(ext, CodeHiliteExtension):
                    self.codehilite_conf = ext.config
                    break

            self.checked_for_codehilite = True
        text = '\n'.join(lines)
        while 1:
            m = FENCED_BLOCK_RE.search(text)
            if m:
                lang = ''
                if m.group('lang'):
                    lang = LANG_TAG % m.group('lang')
                if self.codehilite_conf:
                    highliter = CodeHilite(m.group('code'), linenos=self.codehilite_conf['force_linenos'][0], guess_lang=self.codehilite_conf['guess_lang'][0], css_class=self.codehilite_conf['css_class'][0], style=self.codehilite_conf['pygments_style'][0], lang=m.group('lang') or None, noclasses=self.codehilite_conf['noclasses'][0])
                    code = highliter.hilite()
                else:
                    code = CODE_WRAP % (lang, self._escape(m.group('code')))
                placeholder = self.markdown.htmlStash.store(code, safe=True)
                text = '%s\n%s\n%s' % (text[:m.start()], placeholder, text[m.end():])
            else:
                break

        return text.split('\n')

    def _escape(self, txt):
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt


def makeExtension(configs = None):
    return FencedCodeExtension(configs=configs)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
