#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\inlinepatterns.py
import markdown.util as util
import odict
import re
from urlparse import urlparse, urlunparse
import sys
import htmlentitydefs

def build_inlinepatterns(md_instance, **kwargs):
    inlinePatterns = odict.OrderedDict()
    inlinePatterns['backtick'] = BacktickPattern(BACKTICK_RE)
    inlinePatterns['escape'] = EscapePattern(ESCAPE_RE, md_instance)
    inlinePatterns['reference'] = ReferencePattern(REFERENCE_RE, md_instance)
    inlinePatterns['link'] = LinkPattern(LINK_RE, md_instance)
    inlinePatterns['image_link'] = ImagePattern(IMAGE_LINK_RE, md_instance)
    inlinePatterns['image_reference'] = ImageReferencePattern(IMAGE_REFERENCE_RE, md_instance)
    inlinePatterns['short_reference'] = ReferencePattern(SHORT_REF_RE, md_instance)
    inlinePatterns['autolink'] = AutolinkPattern(AUTOLINK_RE, md_instance)
    inlinePatterns['automail'] = AutomailPattern(AUTOMAIL_RE, md_instance)
    inlinePatterns['linebreak'] = SubstituteTagPattern(LINE_BREAK_RE, 'br')
    if md_instance.safeMode != 'escape':
        inlinePatterns['html'] = HtmlPattern(HTML_RE, md_instance)
    inlinePatterns['entity'] = HtmlPattern(ENTITY_RE, md_instance)
    inlinePatterns['not_strong'] = SimpleTextPattern(NOT_STRONG_RE)
    inlinePatterns['strong_em'] = DoubleTagPattern(STRONG_EM_RE, 'strong,em')
    inlinePatterns['strong'] = SimpleTagPattern(STRONG_RE, 'strong')
    inlinePatterns['emphasis'] = SimpleTagPattern(EMPHASIS_RE, 'em')
    if md_instance.smart_emphasis:
        inlinePatterns['emphasis2'] = SimpleTagPattern(SMART_EMPHASIS_RE, 'em')
    else:
        inlinePatterns['emphasis2'] = SimpleTagPattern(EMPHASIS_2_RE, 'em')
    return inlinePatterns


NOBRACKET = '[^\\]\\[]*'
BRK = '\\[(' + (NOBRACKET + '(\\[') * 6 + (NOBRACKET + '\\])*') * 6 + NOBRACKET + ')\\]'
NOIMG = '(?<!\\!)'
BACKTICK_RE = '(?<!\\\\)(`+)(.+?)(?<!`)\\2(?!`)'
ESCAPE_RE = '\\\\(.)'
EMPHASIS_RE = '(\\*)([^\\*]+)\\2'
STRONG_RE = '(\\*{2}|_{2})(.+?)\\2'
STRONG_EM_RE = '(\\*{3}|_{3})(.+?)\\2'
SMART_EMPHASIS_RE = '(?<!\\w)(_)(?!_)(.+?)(?<!_)\\2(?!\\w)'
EMPHASIS_2_RE = '(_)(.+?)\\2'
LINK_RE = NOIMG + BRK + '\\(\\s*(<.*?>|((?:(?:\\(.*?\\))|[^\\(\\)]))*?)\\s*(([\'"])(.*?)\\12\\s*)?\\)'
IMAGE_LINK_RE = '\\!' + BRK + '\\s*\\((<.*?>|([^\\)]*))\\)'
REFERENCE_RE = NOIMG + BRK + '\\s?\\[([^\\]]*)\\]'
SHORT_REF_RE = NOIMG + '\\[([^\\]]+)\\]'
IMAGE_REFERENCE_RE = '\\!' + BRK + '\\s?\\[([^\\]]*)\\]'
NOT_STRONG_RE = '((^| )(\\*|_)( |$))'
AUTOLINK_RE = '<((?:[Ff]|[Hh][Tt])[Tt][Pp][Ss]?://[^>]*)>'
AUTOMAIL_RE = '<([^> \\!]*@[^> ]*)>'
HTML_RE = '(\\<([a-zA-Z/][^\\>]*?|\\!--.*?--)\\>)'
ENTITY_RE = '(&[\\#a-zA-Z0-9]*;)'
LINE_BREAK_RE = '  \\n'

def dequote(string):
    if string.startswith('"') and string.endswith('"') or string.startswith("'") and string.endswith("'"):
        return string[1:-1]
    else:
        return string


ATTR_RE = re.compile('\\{@([^\\}]*)=([^\\}]*)}')

def handleAttributes(text, parent):

    def attributeCallback(match):
        parent.set(match.group(1), match.group(2).replace('\n', ' '))

    return ATTR_RE.sub(attributeCallback, text)


class Pattern:

    def __init__(self, pattern, markdown_instance = None):
        self.pattern = pattern
        self.compiled_re = re.compile('^(.*?)%s(.*?)$' % pattern, re.DOTALL | re.UNICODE)
        self.safe_mode = False
        if markdown_instance:
            self.markdown = markdown_instance

    def getCompiledRegExp(self):
        return self.compiled_re

    def handleMatch(self, m):
        pass

    def type(self):
        return self.__class__.__name__

    def unescape(self, text):
        try:
            stash = self.markdown.treeprocessors['inline'].stashed_nodes
        except KeyError:
            return text

        def itertext(el):
            tag = el.tag
            if not isinstance(tag, basestring) and tag is not None:
                return
            if el.text:
                yield el.text
            for e in el:
                for s in itertext(e):
                    yield s

                if e.tail:
                    yield e.tail

        def get_stash(m):
            id = m.group(1)
            if id in stash:
                value = stash.get(id)
                if isinstance(value, basestring):
                    return value
                else:
                    return ''.join(itertext(value))

        return util.INLINE_PLACEHOLDER_RE.sub(get_stash, text)


class SimpleTextPattern(Pattern):

    def handleMatch(self, m):
        text = m.group(2)
        if text == util.INLINE_PLACEHOLDER_PREFIX:
            return None
        return text


class EscapePattern(Pattern):

    def handleMatch(self, m):
        char = m.group(2)
        if char in self.markdown.ESCAPED_CHARS:
            return '%s%s%s' % (util.STX, ord(char), util.ETX)
        else:
            return '\\%s' % char


class SimpleTagPattern(Pattern):

    def __init__(self, pattern, tag):
        Pattern.__init__(self, pattern)
        self.tag = tag

    def handleMatch(self, m):
        el = util.etree.Element(self.tag)
        el.text = m.group(3)
        return el


class SubstituteTagPattern(SimpleTagPattern):

    def handleMatch(self, m):
        return util.etree.Element(self.tag)


class BacktickPattern(Pattern):

    def __init__(self, pattern):
        Pattern.__init__(self, pattern)
        self.tag = 'code'

    def handleMatch(self, m):
        el = util.etree.Element(self.tag)
        el.text = util.AtomicString(m.group(3).strip())
        return el


class DoubleTagPattern(SimpleTagPattern):

    def handleMatch(self, m):
        tag1, tag2 = self.tag.split(',')
        el1 = util.etree.Element(tag1)
        el2 = util.etree.SubElement(el1, tag2)
        el2.text = m.group(3)
        return el1


class HtmlPattern(Pattern):

    def handleMatch(self, m):
        rawhtml = self.unescape(m.group(2))
        place_holder = self.markdown.htmlStash.store(rawhtml)
        return place_holder

    def unescape(self, text):
        try:
            stash = self.markdown.treeprocessors['inline'].stashed_nodes
        except KeyError:
            return text

        def get_stash(m):
            id = m.group(1)
            value = stash.get(id)
            if value is not None:
                try:
                    return self.markdown.serializer(value)
                except:
                    return '\\%s' % value

        return util.INLINE_PLACEHOLDER_RE.sub(get_stash, text)


class LinkPattern(Pattern):

    def handleMatch(self, m):
        el = util.etree.Element('a')
        el.text = m.group(2)
        title = m.group(13)
        href = m.group(9)
        if href:
            if href[0] == '<':
                href = href[1:-1]
            el.set('href', self.sanitize_url(self.unescape(href.strip())))
        else:
            el.set('href', '')
        if title:
            title = dequote(self.unescape(title))
            el.set('title', title)
        return el

    def sanitize_url(self, url):
        url = url.replace(' ', '%20')
        if not self.markdown.safeMode:
            return url
        try:
            scheme, netloc, path, params, query, fragment = url = urlparse(url)
        except ValueError:
            return ''

        locless_schemes = ['', 'mailto', 'news']
        if netloc == '' and scheme not in locless_schemes:
            return ''
        for part in url[2:]:
            if ':' in part:
                return ''

        return urlunparse(url)


class ImagePattern(LinkPattern):

    def handleMatch(self, m):
        el = util.etree.Element('img')
        src_parts = m.group(9).split()
        if src_parts:
            src = src_parts[0]
            if src[0] == '<' and src[-1] == '>':
                src = src[1:-1]
            el.set('src', self.sanitize_url(self.unescape(src)))
        else:
            el.set('src', '')
        if len(src_parts) > 1:
            el.set('title', dequote(self.unescape(' '.join(src_parts[1:]))))
        if self.markdown.enable_attributes:
            truealt = handleAttributes(m.group(2), el)
        else:
            truealt = m.group(2)
        el.set('alt', self.unescape(truealt))
        return el


class ReferencePattern(LinkPattern):
    NEWLINE_CLEANUP_RE = re.compile('[ ]?\\n', re.MULTILINE)

    def handleMatch(self, m):
        try:
            id = m.group(9).lower()
        except IndexError:
            id = None

        if not id:
            id = m.group(2).lower()
        id = self.NEWLINE_CLEANUP_RE.sub(' ', id)
        if id not in self.markdown.references:
            return
        href, title = self.markdown.references[id]
        text = m.group(2)
        return self.makeTag(href, title, text)

    def makeTag(self, href, title, text):
        el = util.etree.Element('a')
        el.set('href', self.sanitize_url(href))
        if title:
            el.set('title', title)
        el.text = text
        return el


class ImageReferencePattern(ReferencePattern):

    def makeTag(self, href, title, text):
        el = util.etree.Element('img')
        el.set('src', self.sanitize_url(href))
        if title:
            el.set('title', title)
        el.set('alt', self.unescape(text))
        return el


class AutolinkPattern(Pattern):

    def handleMatch(self, m):
        el = util.etree.Element('a')
        el.set('href', self.unescape(m.group(2)))
        el.text = util.AtomicString(m.group(2))
        return el


class AutomailPattern(Pattern):

    def handleMatch(self, m):
        el = util.etree.Element('a')
        email = self.unescape(m.group(2))
        if email.startswith('mailto:'):
            email = email[len('mailto:'):]

        def codepoint2name(code):
            entity = htmlentitydefs.codepoint2name.get(code)
            if entity:
                return '%s%s;' % (util.AMP_SUBSTITUTE, entity)
            else:
                return '%s#%d;' % (util.AMP_SUBSTITUTE, code)

        letters = [ codepoint2name(ord(letter)) for letter in email ]
        el.text = util.AtomicString(''.join(letters))
        mailto = 'mailto:' + email
        mailto = ''.join([ util.AMP_SUBSTITUTE + '#%d;' % ord(letter) for letter in mailto ])
        el.set('href', mailto)
        return el
