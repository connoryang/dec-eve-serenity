#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\meta.py
import re
import markdown
META_RE = re.compile('^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\\s*(?P<value>.*)')
META_MORE_RE = re.compile('^[ ]{4,}(?P<value>.*)')

class MetaExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('meta', MetaPreprocessor(md), '_begin')


class MetaPreprocessor(markdown.preprocessors.Preprocessor):

    def run(self, lines):
        meta = {}
        key = None
        while 1:
            line = lines.pop(0)
            if line.strip() == '':
                break
            m1 = META_RE.match(line)
            if m1:
                key = m1.group('key').lower().strip()
                value = m1.group('value').strip()
                try:
                    meta[key].append(value)
                except KeyError:
                    meta[key] = [value]

            else:
                m2 = META_MORE_RE.match(line)
                if m2 and key:
                    meta[key].append(m2.group('value').strip())
                else:
                    lines.insert(0, line)
                    break

        self.markdown.Meta = meta
        return lines


def makeExtension(configs = {}):
    return MetaExtension(configs=configs)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
