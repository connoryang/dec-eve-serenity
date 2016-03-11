#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\extra.py
import markdown
extensions = ['smart_strong',
 'fenced_code',
 'footnotes',
 'attr_list',
 'def_list',
 'tables',
 'abbr']

class ExtraExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.registerExtensions(extensions, self.config)
        md.preprocessors['html_block'].markdown_in_raw = True


def makeExtension(configs = {}):
    return ExtraExtension(configs=dict(configs))
