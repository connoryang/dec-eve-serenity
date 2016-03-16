#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\treeprocessors.py
import re
import inlinepatterns
import markdown.util as util
import odict

def build_treeprocessors(md_instance, **kwargs):
    treeprocessors = odict.OrderedDict()
    treeprocessors['inline'] = InlineProcessor(md_instance)
    treeprocessors['prettify'] = PrettifyTreeprocessor(md_instance)
    return treeprocessors


def isString(s):
    if not isinstance(s, util.AtomicString):
        return isinstance(s, basestring)
    return False


class Processor():

    def __init__(self, markdown_instance = None):
        if markdown_instance:
            self.markdown = markdown_instance


class Treeprocessor(Processor):

    def run(self, root):
        pass


class InlineProcessor(Treeprocessor):

    def __init__(self, md):
        self.__placeholder_prefix = util.INLINE_PLACEHOLDER_PREFIX
        self.__placeholder_suffix = util.ETX
        self.__placeholder_length = 4 + len(self.__placeholder_prefix) + len(self.__placeholder_suffix)
        self.__placeholder_re = util.INLINE_PLACEHOLDER_RE
        self.markdown = md

    def __makePlaceholder(self, type):
        id = '%04d' % len(self.stashed_nodes)
        hash = util.INLINE_PLACEHOLDER % id
        return (hash, id)

    def __findPlaceholder(self, data, index):
        m = self.__placeholder_re.search(data, index)
        if m:
            return (m.group(1), m.end())
        else:
            return (None, index + 1)

    def __stashNode(self, node, type):
        placeholder, id = self.__makePlaceholder(type)
        self.stashed_nodes[id] = node
        return placeholder

    def __handleInline(self, data, patternIndex = 0):
        if not isinstance(data, util.AtomicString):
            startIndex = 0
            while patternIndex < len(self.markdown.inlinePatterns):
                data, matched, startIndex = self.__applyPattern(self.markdown.inlinePatterns.value_for_index(patternIndex), data, patternIndex, startIndex)
                if not matched:
                    patternIndex += 1

        return data

    def __processElementText(self, node, subnode, isText = True):
        if isText:
            text = subnode.text
            subnode.text = None
        else:
            text = subnode.tail
            subnode.tail = None
        childResult = self.__processPlaceholders(text, subnode)
        if not isText and node is not subnode:
            pos = node._children.index(subnode)
            node.remove(subnode)
        else:
            pos = 0
        childResult.reverse()
        for newChild in childResult:
            node.insert(pos, newChild)

    def __processPlaceholders(self, data, parent):

        def linkText(text):
            if text:
                if result:
                    if result[-1].tail:
                        result[-1].tail += text
                    else:
                        result[-1].tail = text
                elif parent.text:
                    parent.text += text
                else:
                    parent.text = text

        result = []
        strartIndex = 0
        while data:
            index = data.find(self.__placeholder_prefix, strartIndex)
            if index != -1:
                id, phEndIndex = self.__findPlaceholder(data, index)
                if id in self.stashed_nodes:
                    node = self.stashed_nodes.get(id)
                    if index > 0:
                        text = data[strartIndex:index]
                        linkText(text)
                    if not isString(node):
                        for child in [node] + node._children:
                            if child.tail:
                                if child.tail.strip():
                                    self.__processElementText(node, child, False)
                            if child.text:
                                if child.text.strip():
                                    self.__processElementText(child, child)

                    else:
                        linkText(node)
                        strartIndex = phEndIndex
                        continue
                    strartIndex = phEndIndex
                    result.append(node)
                else:
                    end = index + len(self.__placeholder_prefix)
                    linkText(data[strartIndex:end])
                    strartIndex = end
            else:
                text = data[strartIndex:]
                if isinstance(data, util.AtomicString):
                    text = util.AtomicString(text)
                linkText(text)
                data = ''

        return result

    def __applyPattern(self, pattern, data, patternIndex, startIndex = 0):
        match = pattern.getCompiledRegExp().match(data[startIndex:])
        leftData = data[:startIndex]
        if not match:
            return (data, False, 0)
        node = pattern.handleMatch(match)
        if node is None:
            return (data, True, len(leftData) + match.span(len(match.groups()))[0])
        if not isString(node):
            if not isinstance(node.text, util.AtomicString):
                for child in [node] + node._children:
                    if not isString(node):
                        if child.text:
                            child.text = self.__handleInline(child.text, patternIndex + 1)
                        if child.tail:
                            child.tail = self.__handleInline(child.tail, patternIndex)

        placeholder = self.__stashNode(node, pattern.type())
        return ('%s%s%s%s' % (leftData,
          match.group(1),
          placeholder,
          match.groups()[-1]), True, 0)

    def run(self, tree):
        self.stashed_nodes = {}
        stack = [tree]
        while stack:
            currElement = stack.pop()
            insertQueue = []
            for child in currElement._children:
                if child.text and not isinstance(child.text, util.AtomicString):
                    text = child.text
                    child.text = None
                    lst = self.__processPlaceholders(self.__handleInline(text), child)
                    stack += lst
                    insertQueue.append((child, lst))
                if child.tail:
                    tail = self.__handleInline(child.tail)
                    dumby = util.etree.Element('d')
                    tailResult = self.__processPlaceholders(tail, dumby)
                    if dumby.text:
                        child.tail = dumby.text
                    else:
                        child.tail = None
                    pos = currElement._children.index(child) + 1
                    tailResult.reverse()
                    for newChild in tailResult:
                        currElement.insert(pos, newChild)

                if child._children:
                    stack.append(child)

            for element, lst in insertQueue:
                if self.markdown.enable_attributes:
                    if element.text:
                        element.text = inlinepatterns.handleAttributes(element.text, element)
                i = 0
                for newChild in lst:
                    if self.markdown.enable_attributes:
                        if newChild.tail:
                            newChild.tail = inlinepatterns.handleAttributes(newChild.tail, element)
                        if newChild.text:
                            newChild.text = inlinepatterns.handleAttributes(newChild.text, newChild)
                    element.insert(i, newChild)
                    i += 1

        return tree


class PrettifyTreeprocessor(Treeprocessor):

    def _prettifyETree(self, elem):
        i = '\n'
        if util.isBlockLevel(elem.tag) and elem.tag not in ('code', 'pre'):
            if (not elem.text or not elem.text.strip()) and len(elem) and util.isBlockLevel(elem[0].tag):
                elem.text = i
            for e in elem:
                if util.isBlockLevel(e.tag):
                    self._prettifyETree(e)

            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        if not elem.tail or not elem.tail.strip():
            elem.tail = i

    def run(self, root):
        self._prettifyETree(root)
        brs = root.iter('br')
        for br in brs:
            if not br.tail or not br.tail.strip():
                br.tail = '\n'
            else:
                br.tail = '\n%s' % br.tail
