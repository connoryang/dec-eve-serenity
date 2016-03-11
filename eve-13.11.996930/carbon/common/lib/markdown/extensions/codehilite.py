#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\codehilite.py
import markdown
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
    from pygments.formatters import HtmlFormatter
    pygments = True
except ImportError:
    pygments = False

class CodeHilite:

    def __init__(self, src = None, linenos = False, guess_lang = True, css_class = 'codehilite', lang = None, style = 'default', noclasses = False, tab_length = 4):
        self.src = src
        self.lang = lang
        self.linenos = linenos
        self.guess_lang = guess_lang
        self.css_class = css_class
        self.style = style
        self.noclasses = noclasses
        self.tab_length = tab_length

    def hilite(self):
        self.src = self.src.strip('\n')
        if self.lang is None:
            self._getLang()
        if pygments:
            try:
                lexer = get_lexer_by_name(self.lang)
            except ValueError:
                try:
                    if self.guess_lang:
                        lexer = guess_lexer(self.src)
                    else:
                        lexer = TextLexer()
                except ValueError:
                    lexer = TextLexer()

            formatter = HtmlFormatter(linenos=self.linenos, cssclass=self.css_class, style=self.style, noclasses=self.noclasses)
            return highlight(self.src, lexer, formatter)
        else:
            txt = self.src.replace('&', '&amp;')
            txt = txt.replace('<', '&lt;')
            txt = txt.replace('>', '&gt;')
            txt = txt.replace('"', '&quot;')
            classes = []
            if self.lang:
                classes.append('language-%s' % self.lang)
            if self.linenos:
                classes.append('linenums')
            class_str = ''
            if classes:
                class_str = ' class="%s"' % ' '.join(classes)
            return '<pre class="%s"><code%s>%s</code></pre>\n' % (self.css_class, class_str, txt)

    def _getLang(self):
        import re
        lines = self.src.split('\n')
        fl = lines.pop(0)
        c = re.compile('\n            (?:(?:^::+)|(?P<shebang>^[#]!))\t# Shebang or 2 or more colons.\n            (?P<path>(?:/\\w+)*[/ ])?        # Zero or 1 path\n            (?P<lang>[\\w+-]*)               # The language\n            ', re.VERBOSE)
        m = c.search(fl)
        if m:
            try:
                self.lang = m.group('lang').lower()
            except IndexError:
                self.lang = None

            if m.group('path'):
                lines.insert(0, fl)
            if m.group('shebang'):
                self.linenos = True
        else:
            lines.insert(0, fl)
        self.src = '\n'.join(lines).strip('\n')


class HiliteTreeprocessor(markdown.treeprocessors.Treeprocessor):

    def run(self, root):
        blocks = root.getiterator('pre')
        for block in blocks:
            children = block._children
            if len(children) == 1 and children[0].tag == 'code':
                code = CodeHilite(children[0].text, linenos=self.config['force_linenos'], guess_lang=self.config['guess_lang'], css_class=self.config['css_class'], style=self.config['pygments_style'], noclasses=self.config['noclasses'], tab_length=self.markdown.tab_length)
                placeholder = self.markdown.htmlStash.store(code.hilite(), safe=True)
                block.clear()
                block.tag = 'p'
                block.text = placeholder


class CodeHiliteExtension(markdown.Extension):

    def __init__(self, configs):
        self.config = {'force_linenos': [False, 'Force line numbers - Default: False'],
         'guess_lang': [True, 'Automatic language detection - Default: True'],
         'css_class': ['codehilite', 'Set class name for wrapper <div> - Default: codehilite'],
         'pygments_style': ['default', 'Pygments HTML Formatter Style (Colorscheme) - Default: default'],
         'noclasses': [False, 'Use inline styles instead of CSS classes - Default false']}
        for key, value in configs:
            if value == 'True':
                value = True
            if value == 'False':
                value = False
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        hiliter = HiliteTreeprocessor(md)
        hiliter.config = self.getConfigs()
        md.treeprocessors.add('hilite', hiliter, '<inline')
        md.registerExtension(self)


def makeExtension(configs = {}):
    return CodeHiliteExtension(configs=configs)
