#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\sane_lists.py
import re
import markdown

class SaneOListProcessor(markdown.blockprocessors.OListProcessor):
    CHILD_RE = re.compile('^[ ]{0,3}((\\d+\\.))[ ]+(.*)')
    SIBLING_TAGS = ['ol']


class SaneUListProcessor(markdown.blockprocessors.UListProcessor):
    CHILD_RE = re.compile('^[ ]{0,3}(([*+-]))[ ]+(.*)')
    SIBLING_TAGS = ['ul']


class SaneListExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors['olist'] = SaneOListProcessor(md.parser)
        md.parser.blockprocessors['ulist'] = SaneUListProcessor(md.parser)


def makeExtension(configs = {}):
    return SaneListExtension(configs=configs)
