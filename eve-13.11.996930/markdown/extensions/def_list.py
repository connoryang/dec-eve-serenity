#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\def_list.py
import re
import markdown
from markdown.util import etree

class DefListProcessor(markdown.blockprocessors.BlockProcessor):
    RE = re.compile('(^|\\n)[ ]{0,3}:[ ]{1,3}(.*?)(\\n|$)')
    NO_INDENT_RE = re.compile('^[ ]{0,3}[^ :]')

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)
        terms = [ l.strip() for l in block[:m.start()].split('\n') if l.strip() ]
        block = block[m.end():]
        no_indent = self.NO_INDENT_RE.match(block)
        if no_indent:
            d, theRest = block, None
        else:
            d, theRest = self.detab(block)
        if d:
            d = '%s\n%s' % (m.group(2), d)
        else:
            d = m.group(2)
        sibling = self.lastChild(parent)
        if not terms and sibling.tag == 'p':
            state = 'looselist'
            terms = sibling.text.split('\n')
            parent.remove(sibling)
            sibling = self.lastChild(parent)
        else:
            state = 'list'
        if sibling and sibling.tag == 'dl':
            dl = sibling
            if len(dl) and dl[-1].tag == 'dd' and len(dl[-1]):
                state = 'looselist'
        else:
            dl = etree.SubElement(parent, 'dl')
        for term in terms:
            dt = etree.SubElement(dl, 'dt')
            dt.text = term

        self.parser.state.set(state)
        dd = etree.SubElement(dl, 'dd')
        self.parser.parseBlocks(dd, [d])
        self.parser.state.reset()
        if theRest:
            blocks.insert(0, theRest)


class DefListIndentProcessor(markdown.blockprocessors.ListIndentProcessor):
    ITEM_TYPES = ['dd']
    LIST_TYPES = ['dl']

    def create_item(self, parent, block):
        dd = markdown.etree.SubElement(parent, 'dd')
        self.parser.parseBlocks(dd, [block])


class DefListExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors.add('defindent', DefListIndentProcessor(md.parser), '>indent')
        md.parser.blockprocessors.add('deflist', DefListProcessor(md.parser), '>ulist')


def makeExtension(configs = {}):
    return DefListExtension(configs=configs)
