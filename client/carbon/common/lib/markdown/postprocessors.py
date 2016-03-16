#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\postprocessors.py
import re
import markdown.util as util
import odict

def build_postprocessors(md_instance, **kwargs):
    postprocessors = odict.OrderedDict()
    postprocessors['raw_html'] = RawHtmlPostprocessor(md_instance)
    postprocessors['amp_substitute'] = AndSubstitutePostprocessor()
    postprocessors['unescape'] = UnescapePostprocessor()
    return postprocessors


class Postprocessor(util.Processor):

    def run(self, text):
        pass


class RawHtmlPostprocessor(Postprocessor):

    def run(self, text):
        for i in range(self.markdown.htmlStash.html_counter):
            html, safe = self.markdown.htmlStash.rawHtmlBlocks[i]
            if self.markdown.safeMode and not safe:
                if str(self.markdown.safeMode).lower() == 'escape':
                    html = self.escape(html)
                elif str(self.markdown.safeMode).lower() == 'remove':
                    html = ''
                else:
                    html = self.markdown.html_replacement_text
            if self.isblocklevel(html) and (safe or not self.markdown.safeMode):
                text = text.replace('<p>%s</p>' % self.markdown.htmlStash.get_placeholder(i), html + '\n')
            text = text.replace(self.markdown.htmlStash.get_placeholder(i), html)

        return text

    def escape(self, html):
        html = html.replace('&', '&amp;')
        html = html.replace('<', '&lt;')
        html = html.replace('>', '&gt;')
        return html.replace('"', '&quot;')

    def isblocklevel(self, html):
        m = re.match('^\\<\\/?([^ >]+)', html)
        if m:
            if m.group(1)[0] in ('!', '?', '@', '%'):
                return True
            return util.isBlockLevel(m.group(1))
        return False


class AndSubstitutePostprocessor(Postprocessor):

    def run(self, text):
        text = text.replace(util.AMP_SUBSTITUTE, '&')
        return text


class UnescapePostprocessor(Postprocessor):
    RE = re.compile('%s(\\d+)%s' % (util.STX, util.ETX))

    def unescape(self, m):
        return unichr(int(m.group(1)))

    def run(self, text):
        return self.RE.sub(self.unescape, text)
