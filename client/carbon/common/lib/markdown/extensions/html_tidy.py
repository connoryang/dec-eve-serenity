#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\html_tidy.py
import markdown
try:
    import tidy
except ImportError:
    tidy = None

class TidyExtension(markdown.Extension):

    def __init__(self, configs):
        self.config = dict(output_xhtml=1, show_body_only=1, char_encoding='utf8')
        for c in configs:
            self.config[c[0]] = c[1]

    def extendMarkdown(self, md, md_globals):
        md.tidy_options = self.config
        if tidy:
            md.postprocessors['tidy'] = TidyProcessor(md)


class TidyProcessor(markdown.postprocessors.Postprocessor):

    def run(self, text):
        enc = self.markdown.tidy_options.get('char_encoding', 'utf8')
        return unicode(tidy.parseString(text.encode(enc), **self.markdown.tidy_options), encoding=enc)


def makeExtension(configs = None):
    return TidyExtension(configs=configs)
