#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\blockparser.py
import markdown.util as util
import odict

class State(list):

    def set(self, state):
        self.append(state)

    def reset(self):
        self.pop()

    def isstate(self, state):
        if len(self):
            return self[-1] == state
        else:
            return False


class BlockParser:

    def __init__(self, markdown):
        self.blockprocessors = odict.OrderedDict()
        self.state = State()
        self.markdown = markdown

    def parseDocument(self, lines):
        self.root = util.etree.Element(self.markdown.doc_tag)
        self.parseChunk(self.root, '\n'.join(lines))
        return util.etree.ElementTree(self.root)

    def parseChunk(self, parent, text):
        self.parseBlocks(parent, text.split('\n\n'))

    def parseBlocks(self, parent, blocks):
        while blocks:
            for processor in self.blockprocessors.values():
                if processor.test(parent, blocks[0]):
                    if processor.run(parent, blocks) is not False:
                        break
