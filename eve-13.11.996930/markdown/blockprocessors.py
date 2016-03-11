#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\blockprocessors.py
import logging
import re
import markdown.util as util
from blockparser import BlockParser
logger = logging.getLogger('MARKDOWN')

def build_block_parser(md_instance, **kwargs):
    parser = BlockParser(md_instance)
    parser.blockprocessors['empty'] = EmptyBlockProcessor(parser)
    parser.blockprocessors['indent'] = ListIndentProcessor(parser)
    parser.blockprocessors['code'] = CodeBlockProcessor(parser)
    parser.blockprocessors['hashheader'] = HashHeaderProcessor(parser)
    parser.blockprocessors['setextheader'] = SetextHeaderProcessor(parser)
    parser.blockprocessors['hr'] = HRProcessor(parser)
    parser.blockprocessors['olist'] = OListProcessor(parser)
    parser.blockprocessors['ulist'] = UListProcessor(parser)
    parser.blockprocessors['quote'] = BlockQuoteProcessor(parser)
    parser.blockprocessors['paragraph'] = ParagraphProcessor(parser)
    return parser


class BlockProcessor:

    def __init__(self, parser):
        self.parser = parser
        self.tab_length = parser.markdown.tab_length

    def lastChild(self, parent):
        if len(parent):
            return parent[-1]
        else:
            return None

    def detab(self, text):
        newtext = []
        lines = text.split('\n')
        for line in lines:
            if line.startswith(' ' * self.tab_length):
                newtext.append(line[self.tab_length:])
            elif not line.strip():
                newtext.append('')
            else:
                break

        return ('\n'.join(newtext), '\n'.join(lines[len(newtext):]))

    def looseDetab(self, text, level = 1):
        lines = text.split('\n')
        for i in range(len(lines)):
            if lines[i].startswith(' ' * self.tab_length * level):
                lines[i] = lines[i][self.tab_length * level:]

        return '\n'.join(lines)

    def test(self, parent, block):
        pass

    def run(self, parent, blocks):
        pass


class ListIndentProcessor(BlockProcessor):
    ITEM_TYPES = ['li']
    LIST_TYPES = ['ul', 'ol']

    def __init__(self, *args):
        BlockProcessor.__init__(self, *args)
        self.INDENT_RE = re.compile('^(([ ]{%s})+)' % self.tab_length)

    def test(self, parent, block):
        return block.startswith(' ' * self.tab_length) and not self.parser.state.isstate('detabbed') and (parent.tag in self.ITEM_TYPES or len(parent) and parent[-1] and parent[-1].tag in self.LIST_TYPES)

    def run(self, parent, blocks):
        block = blocks.pop(0)
        level, sibling = self.get_level(parent, block)
        block = self.looseDetab(block, level)
        self.parser.state.set('detabbed')
        if parent.tag in self.ITEM_TYPES:
            if len(parent) and parent[-1].tag in self.LIST_TYPES:
                self.parser.parseBlocks(parent[-1], [block])
            else:
                self.parser.parseBlocks(parent, [block])
        elif sibling.tag in self.ITEM_TYPES:
            self.parser.parseBlocks(sibling, [block])
        elif len(sibling) and sibling[-1].tag in self.ITEM_TYPES:
            if sibling[-1].text:
                p = util.etree.Element('p')
                p.text = sibling[-1].text
                sibling[-1].text = ''
                sibling[-1].insert(0, p)
            self.parser.parseChunk(sibling[-1], block)
        else:
            self.create_item(sibling, block)
        self.parser.state.reset()

    def create_item(self, parent, block):
        li = util.etree.SubElement(parent, 'li')
        self.parser.parseBlocks(li, [block])

    def get_level(self, parent, block):
        m = self.INDENT_RE.match(block)
        if m:
            indent_level = len(m.group(1)) / self.tab_length
        else:
            indent_level = 0
        if self.parser.state.isstate('list'):
            level = 1
        else:
            level = 0
        while indent_level > level:
            child = self.lastChild(parent)
            if child and (child.tag in self.LIST_TYPES or child.tag in self.ITEM_TYPES):
                if child.tag in self.LIST_TYPES:
                    level += 1
                parent = child
            else:
                break

        return (level, parent)


class CodeBlockProcessor(BlockProcessor):

    def test(self, parent, block):
        return block.startswith(' ' * self.tab_length)

    def run(self, parent, blocks):
        sibling = self.lastChild(parent)
        block = blocks.pop(0)
        theRest = ''
        if sibling and sibling.tag == 'pre' and len(sibling) and sibling[0].tag == 'code':
            code = sibling[0]
            block, theRest = self.detab(block)
            code.text = util.AtomicString('%s\n%s\n' % (code.text, block.rstrip()))
        else:
            pre = util.etree.SubElement(parent, 'pre')
            code = util.etree.SubElement(pre, 'code')
            block, theRest = self.detab(block)
            code.text = util.AtomicString('%s\n' % block.rstrip())
        if theRest:
            blocks.insert(0, theRest)


class BlockQuoteProcessor(BlockProcessor):
    RE = re.compile('(^|\\n)[ ]{0,3}>[ ]?(.*)')

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)
        if m:
            before = block[:m.start()]
            self.parser.parseBlocks(parent, [before])
            block = '\n'.join([ self.clean(line) for line in block[m.start():].split('\n') ])
        sibling = self.lastChild(parent)
        if sibling and sibling.tag == 'blockquote':
            quote = sibling
        else:
            quote = util.etree.SubElement(parent, 'blockquote')
        self.parser.state.set('blockquote')
        self.parser.parseChunk(quote, block)
        self.parser.state.reset()

    def clean(self, line):
        m = self.RE.match(line)
        if line.strip() == '>':
            return ''
        elif m:
            return m.group(2)
        else:
            return line


class OListProcessor(BlockProcessor):
    TAG = 'ol'
    RE = re.compile('^[ ]{0,3}\\d+\\.[ ]+(.*)')
    CHILD_RE = re.compile('^[ ]{0,3}((\\d+\\.)|[*+-])[ ]+(.*)')
    INDENT_RE = re.compile('^[ ]{4,7}((\\d+\\.)|[*+-])[ ]+.*')
    STARTSWITH = '1'
    SIBLING_TAGS = ['ol', 'ul']

    def test(self, parent, block):
        return bool(self.RE.match(block))

    def run(self, parent, blocks):
        items = self.get_items(blocks.pop(0))
        sibling = self.lastChild(parent)
        if sibling is not None and sibling.tag in self.SIBLING_TAGS:
            lst = sibling
            if lst[-1].text:
                p = util.etree.Element('p')
                p.text = lst[-1].text
                lst[-1].text = ''
                lst[-1].insert(0, p)
            lch = self.lastChild(lst[-1])
            if lch is not None and lch.tail:
                p = util.etree.SubElement(lst[-1], 'p')
                p.text = lch.tail.lstrip()
                lch.tail = ''
            li = util.etree.SubElement(lst, 'li')
            self.parser.state.set('looselist')
            firstitem = items.pop(0)
            self.parser.parseBlocks(li, [firstitem])
            self.parser.state.reset()
        elif parent.tag in ('ol', 'ul'):
            lst = parent
        else:
            lst = util.etree.SubElement(parent, self.TAG)
            if not self.parser.markdown.lazy_ol and self.STARTSWITH != '1':
                lst.attrib['start'] = self.STARTSWITH
        self.parser.state.set('list')
        for item in items:
            if item.startswith(' ' * self.tab_length):
                self.parser.parseBlocks(lst[-1], [item])
            else:
                li = util.etree.SubElement(lst, 'li')
                self.parser.parseBlocks(li, [item])

        self.parser.state.reset()

    def get_items(self, block):
        items = []
        for line in block.split('\n'):
            m = self.CHILD_RE.match(line)
            if m:
                if not items and self.TAG == 'ol':
                    INTEGER_RE = re.compile('(\\d+)')
                    self.STARTSWITH = INTEGER_RE.match(m.group(1)).group()
                items.append(m.group(3))
            elif self.INDENT_RE.match(line):
                if items[-1].startswith(' ' * self.tab_length):
                    items[-1] = '%s\n%s' % (items[-1], line)
                else:
                    items.append(line)
            else:
                items[-1] = '%s\n%s' % (items[-1], line)

        return items


class UListProcessor(OListProcessor):
    TAG = 'ul'
    RE = re.compile('^[ ]{0,3}[*+-][ ]+(.*)')


class HashHeaderProcessor(BlockProcessor):
    RE = re.compile('(^|\\n)(?P<level>#{1,6})(?P<header>.*?)#*(\\n|$)')

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)
        if m:
            before = block[:m.start()]
            after = block[m.end():]
            if before:
                self.parser.parseBlocks(parent, [before])
            h = util.etree.SubElement(parent, 'h%d' % len(m.group('level')))
            h.text = m.group('header').strip()
            if after:
                blocks.insert(0, after)
        else:
            logger.warn("We've got a problem header: %r" % block)


class SetextHeaderProcessor(BlockProcessor):
    RE = re.compile('^.*?\\n[=-]+[ ]*(\\n|$)', re.MULTILINE)

    def test(self, parent, block):
        return bool(self.RE.match(block))

    def run(self, parent, blocks):
        lines = blocks.pop(0).split('\n')
        if lines[1].startswith('='):
            level = 1
        else:
            level = 2
        h = util.etree.SubElement(parent, 'h%d' % level)
        h.text = lines[0].strip()
        if len(lines) > 2:
            blocks.insert(0, '\n'.join(lines[2:]))


class HRProcessor(BlockProcessor):
    RE = '^[ ]{0,3}((-+[ ]{0,2}){3,}|(_+[ ]{0,2}){3,}|(\\*+[ ]{0,2}){3,})[ ]*'
    SEARCH_RE = re.compile(RE, re.MULTILINE)

    def test(self, parent, block):
        m = self.SEARCH_RE.search(block)
        if m and (m.end() == len(block) or block[m.end()] == '\n'):
            self.match = m
            return True
        return False

    def run(self, parent, blocks):
        block = blocks.pop(0)
        prelines = block[:self.match.start()].rstrip('\n')
        if prelines:
            self.parser.parseBlocks(parent, [prelines])
        hr = util.etree.SubElement(parent, 'hr')
        postlines = block[self.match.end():].lstrip('\n')
        if postlines:
            blocks.insert(0, postlines)


class EmptyBlockProcessor(BlockProcessor):
    RE = re.compile('^\\s*\\n')

    def test(self, parent, block):
        return bool(self.RE.match(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.match(block)
        if m:
            blocks.insert(0, block[m.end():])
            sibling = self.lastChild(parent)
            if sibling and sibling.tag == 'pre' and sibling[0] and sibling[0].tag == 'code':
                sibling[0].text = util.AtomicString('%s/n/n/n' % sibling[0].text)


class ParagraphProcessor(BlockProcessor):

    def test(self, parent, block):
        return True

    def run(self, parent, blocks):
        block = blocks.pop(0)
        if block.strip():
            if self.parser.state.isstate('list'):
                sibling = self.lastChild(parent)
                if sibling is not None:
                    if sibling.tail:
                        sibling.tail = '%s\n%s' % (sibling.tail, block)
                    else:
                        sibling.tail = '\n%s' % block
                elif parent.text:
                    parent.text = '%s\n%s' % (parent.text, block)
                else:
                    parent.text = block.lstrip()
            else:
                p = util.etree.SubElement(parent, 'p')
                p.text = block.lstrip()
