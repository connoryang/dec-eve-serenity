#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\scriber\htmlutils.py
import re
import HTMLParser
import typeutils
from scriber import const
from inventorycommon import const as iconst

class TolerantParser(HTMLParser.HTMLParser):
    ON_ERROR_THROW = 0
    ON_ERROR_REPLACE = 1
    ON_ERROR_SKIP = 2

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.on_error = self.ON_ERROR_REPLACE
        self.parse_errors = []

    def on_error_replace_with(self):
        return '&lt;'

    def parse_starttag(self, i):
        try:
            return HTMLParser.HTMLParser.parse_starttag(self, i)
        except HTMLParser.HTMLParseError as e:
            self.parse_errors.append(e)
            if self.on_error == self.ON_ERROR_REPLACE:
                self.handle_data(self.on_error_replace_with())
                return i + 1
            if self.on_error == self.ON_ERROR_SKIP:
                return i + 1
            raise

    def parse_endtag(self, i):
        try:
            return HTMLParser.HTMLParser.parse_endtag(self, i)
        except HTMLParser.HTMLParseError as e:
            self.parse_errors.append(e)
            if self.on_error == self.ON_ERROR_REPLACE:
                self.handle_data(self.on_error_replace_with())
                return i + 1
            if self.on_error == self.ON_ERROR_SKIP:
                return i + 1
            raise

    def unknown_decl(self, data):
        pass

    def goahead(self, end):
        rawdata = self.rawdata
        i = 0
        n = len(rawdata)
        while i < n:
            match = self.interesting.search(rawdata, i)
            if match:
                j = match.start()
            else:
                j = n
            if i < j:
                self.handle_data(rawdata[i:j])
            i = self.updatepos(i, j)
            if i == n:
                break
            startswith = rawdata.startswith
            if startswith('<', i):
                if HTMLParser.starttagopen.match(rawdata, i):
                    k = self.parse_starttag(i)
                elif startswith('</', i):
                    k = self.parse_endtag(i)
                elif startswith('<!--', i):
                    k = self.parse_comment(i)
                elif startswith('<?', i):
                    k = self.parse_pi(i)
                elif startswith('<!', i):
                    k = self.parse_declaration(i)
                elif i + 1 < n:
                    self.handle_data('<')
                    k = i + 1
                else:
                    break
                if k < 0:
                    if end:
                        self.error('EOF in middle of construct')
                    break
                i = self.updatepos(i, k)
            elif startswith('&#', i):
                match = HTMLParser.charref.match(rawdata, i)
                if match:
                    name = match.group()[2:-1]
                    k = match.end()
                    if not startswith(';', k - 1):
                        self.handle_data('&#' + name)
                        k = k - 1
                    else:
                        self.handle_charref(name)
                    i = self.updatepos(i, k)
                    continue
                else:
                    if ';' in rawdata[i:]:
                        self.handle_data(rawdata[0:2])
                        i = self.updatepos(i, 2)
                    break
            elif startswith('&', i):
                match = HTMLParser.entityref.match(rawdata, i)
                if match:
                    name = match.group(1)
                    k = match.end()
                    if not startswith(';', k - 1):
                        self.handle_data('&' + name)
                        k = k - 1
                    else:
                        self.handle_entityref(name)
                    i = self.updatepos(i, k)
                    continue
                match = HTMLParser.incomplete.match(rawdata, i)
                if match:
                    self.handle_data(rawdata[i:])
                    if end and match.group() == rawdata[i:]:
                        self.error('EOF in middle of entity or char ref')
                    break
                elif i + 1 < n:
                    self.handle_data('&')
                    i = self.updatepos(i, i + 1)
                else:
                    self.handle_data('&')
                    break

        if end and i < n:
            self.handle_data(rawdata[i:n])
            i = self.updatepos(i, n)
        self.rawdata = rawdata[i:]


class TagStripper(TolerantParser):

    def __init__(self, tag_list = tuple(), preserve_content_list = tuple()):
        TolerantParser.__init__(self)
        self._stripped = []
        self.tag_list = tag_list
        self.preserve_content_list = preserve_content_list
        self.ignore_content_until = None

    def handle_data(self, data):
        if not self.ignore_content_until:
            self._stripped.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in self.tag_list:
            if tag not in self.preserve_content_list:
                self.ignore_content_until = tag
        else:
            attributes = ''
            if attrs:
                attributes = ' %s' % attr_str(attrs)
            self._stripped.append('<%s%s>' % (tag, attributes))

    def handle_endtag(self, tag):
        if self.ignore_content_until == tag:
            self.ignore_content_until = None
        if tag not in self.tag_list:
            self._stripped.append('</%s>' % tag)

    def handle_entityref(self, name):
        if not self.ignore_content_until:
            self._stripped.append('&%s;' % name)

    def handle_charref(self, name):
        if not self.ignore_content_until:
            self._stripped.append('&#%s;' % name)

    def get_stripped(self):
        return ''.join(self._stripped)

    def flush_stripped(self):
        text = self.get_stripped()
        self._stripped = []
        return text


class HTMLStripper(TolerantParser):
    HTML_WHITESPACE = '[ \\t\\r\\n]+'
    HTML_BREAKS = '( \\n|\\n )'
    HTML_NON_CONTENT_TAGS = ['head',
     'script',
     'style',
     'embed',
     'frameset',
     'object',
     'iframe',
     'source',
     'track',
     'video',
     'audio',
     'canvas',
     'meta']

    def __init__(self, preserve_links = True, preserve_images = False, decode_chars = True, error_tolerance = True):
        TolerantParser.__init__(self)
        self._text = []
        self.preserve_links = preserve_links
        self.preserve_images = preserve_images
        self.decode_chars = decode_chars
        self.error_tolerance = error_tolerance
        self.link = ''
        self.ignore_content_until = None

    def handle_data(self, data):
        if not self.ignore_content_until:
            self._text.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in self.HTML_NON_CONTENT_TAGS:
            self.ignore_content_until = tag
        if tag == 'a':
            if self.preserve_links and attrs:
                attrs = dict(attrs)
                self.link = attrs.get('href', '')
        if tag == 'img':
            if self.preserve_images and attrs:
                attrs = dict(attrs)
                self._text.append('[%s]' % attrs.get('src', ''))
        elif tag == 'br':
            self._add_linefeed()

    def handle_endtag(self, tag):
        if self.ignore_content_until == tag:
            self.ignore_content_until = None
        if tag in ('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._add_linefeed(2)
        elif tag == 'a' and self.preserve_links and self.link:
            self._text.append(' [%s]' % self.link)
            self.link = ''

    def handle_entityref(self, name):
        if not self.ignore_content_until:
            code = '&%s;' % name
            if self.decode_chars:
                code = self.unescape(code)
            self._text.append(code)

    def handle_charref(self, name):
        if not self.ignore_content_until:
            code = '&#%s;' % name
            if self.decode_chars:
                code = self.unescape(code)
            self._text.append(code)

    def on_error_replace_with(self):
        if self.decode_chars:
            return '['
        else:
            return '&lt;'

    def _add_linefeed(self, count = 1):
        self._text.append('{{LF}}' * count)

    def get_text(self):
        text = ''.join(self._text)
        text = re.sub(self.HTML_WHITESPACE, ' ', text)
        text = text.replace('{{LF}}', '\n')
        text = re.sub(self.HTML_BREAKS, '\n', text)
        return text.strip()

    def flush_text(self):
        text = self.get_text()
        self._text = []
        return text


def strip_html(html_string, preserve_links = True, preserve_images = False, decode_chars = True):
    stripper = HTMLStripper(preserve_links, preserve_images, decode_chars)
    stripper.feed(html_string)
    return stripper.get_text()


def newline_to_html(string):
    return '<p>%s</p>' % reduce(lambda h, n: h.replace(*n), (('\r', ''), ('\n\n', '</p><p>'), ('\n', '<br />')), string)


def sanitize(html_string):
    return reduce(lambda string, params: string.replace(*params), (('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;')), html_string)


def unsanitize(string):
    return reduce(lambda string, params: string.replace(*params), (('&gt;', '>'), ('&lt;', '<'), ('&amp;', '&')), string)


def esc_email_tags(html, replacer = const.EMAIL_TAG_REPLACE_HTML):
    return const.EMAIL_TAG_GRABBER.sub(replacer, html)


def strip_bad_tags(html_string):
    stripper = TagStripper(HTMLStripper.HTML_NON_CONTENT_TAGS)
    stripper.feed(html_string)
    return stripper.get_stripped()


def attr_str(attribute_list, xhtml_strict = False):
    buff = []
    if isinstance(attribute_list, dict):
        attribute_list = attribute_list.items()
    for attr in attribute_list:
        if len(attr) > 1:
            buff.append('%s="%s"' % (attr[0], attr[1]))
        elif xhtml_strict:
            buff.append('%s="%s"' % (attr[0], attr[0]))
        else:
            buff.append('%s' % attr[0])

    return ' '.join(buff)


def parse_user_notes(raw_notes):
    raw_notes = parse_markdown_link(raw_notes)
    i = 0
    parsed_notes = []
    for m in const.NOTE_LINK_A_HREF_MATCHER.finditer(raw_notes):
        parsed_notes.append(parse_note_auto_link(raw_notes[i:m.start()]))
        parsed_notes.append(m.group(0))
        i = m.end()

    parsed_notes.append(parse_note_auto_link(raw_notes[i:]))
    return ''.join(parsed_notes).replace('\n', '<br>')


def parse_markdown_link(raw_text):
    return re.sub(const.NOTE_LINK_MARKDOWN_PATTERN, const.NOTE_LINK_MARKDOWN_REPLACE, raw_text)


def parse_note_auto_link(raw_text):
    i = 0
    parsed_text = []
    for m in const.NOTE_LINK_AUTO_LINKER.finditer(raw_text):
        parsed_text.append(raw_text[i:m.start()])
        parsed_text.append(const.NOTE_LINK_AUTO_LINK.format(url=_get_ticket_url(m.group(3)), text='%s%s%s' % (m.group(1), m.group(2), m.group(3))))
        i = m.end()

    parsed_text.append(raw_text[i:])
    return ''.join(parsed_text)


def _get_ticket_url(ticket_id):
    ticket_id = typeutils.int_eval(ticket_id)
    if ticket_id > const.OLD_TICKET_ID_THRESHOLD:
        return const.OLD_TICKET_URL.format(ticketID=ticket_id)
    return const.TICKET_URL.format(ticketID=ticket_id)


def strip_extra_amp(string):
    return re.sub(const.EXTRA_AMP_MATCHER, const.EXTRA_AMP_REPLACER, string)


def esp_item_link(item):
    if item.item_type.category_id == iconst.categoryOwner:
        if item.item_type.group_id == iconst.groupCharacter:
            return '/gm/character.py?action=Character&characterID=%d' % item.item_id
        if item.item_type.group_id == iconst.groupCorporation:
            return '/gm/corporation.py?action=Corporation&corporationID=%d' % item.item_id
        if item.item_type.group_id == iconst.groupAlliance:
            return '/gm/alliance.py?action=Alliance&allianceID=%d' % item.item_id
        if item.item_type.group_id == iconst.groupFaction:
            return '/gm/faction.py?action=Faction&factionID=%d' % item.item_id
    elif item.item_type.category_id == iconst.categoryCelestial:
        if item.item_type.group_id == iconst.groupRegion:
            return '/gd/universe.py?action=Region&regionID=%d' % item.item_id
        elif item.item_type.group_id == iconst.groupConstellation:
            return '/gd/universe.py?action=Constellation&constellationID=%s' % item.item_id
        elif item.item_type.group_id == iconst.groupSolarSystem:
            return '/gd/universe.py?action=System&systemID=%d' % item.item_id
        elif item.item_type.group_id == iconst.groupAsteroidBelt:
            return '/gd/universe.py?action=AsteroidBelt&asteroidBeltID=%d' % item.item_id
        else:
            return '/gd/universe.py?action=Celestial&celestialID=%d' % item.item_id
    elif item.item_type.category_id == iconst.categoryStation:
        if item.item_type.group_id == iconst.groupStation:
            return '/gm/stations.py?action=Station&stationID=%d' % item.item_id
    else:
        if item.item_type.category_id == iconst.categorySovereigntyStructure:
            return '/gm/starbase.py?action=Starbase&towerID=' % item.item_id
        if item.item_type.category_id == iconst.categoryShip:
            return '/gm/character.py?action=Ship&characterID=%d&shipID=%d' % (item.owner_id, item.item_id)
    return '/gm/inventory.py?action=Item&itemID=%d' % item.item_id
