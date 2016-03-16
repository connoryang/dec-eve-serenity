#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\nl2br.py
import markdown
BR_RE = '\\n'

class Nl2BrExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        br_tag = markdown.inlinepatterns.SubstituteTagPattern(BR_RE, 'br')
        md.inlinePatterns.add('nl', br_tag, '_end')


def makeExtension(configs = None):
    return Nl2BrExtension(configs)
