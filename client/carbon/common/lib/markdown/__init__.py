#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\__init__.py
version = '2.2.1'
version_info = (2,
 2,
 1,
 'final')
import re
import codecs
import sys
import logging
import warnings
import markdown.util as util
from preprocessors import build_preprocessors
from blockprocessors import build_block_parser
from treeprocessors import build_treeprocessors
from inlinepatterns import build_inlinepatterns
from postprocessors import build_postprocessors
from extensions import Extension
from serializers import to_html_string, to_xhtml_string
__all__ = ['Markdown', 'markdown', 'markdownFromFile']
logger = logging.getLogger('MARKDOWN')

class Markdown():
    doc_tag = 'div'
    option_defaults = {'html_replacement_text': '[HTML_REMOVED]',
     'tab_length': 4,
     'enable_attributes': True,
     'smart_emphasis': True,
     'lazy_ol': True}
    output_formats = {'html': to_html_string,
     'html4': to_html_string,
     'html5': to_html_string,
     'xhtml': to_xhtml_string,
     'xhtml1': to_xhtml_string,
     'xhtml5': to_xhtml_string}
    ESCAPED_CHARS = ['\\',
     '`',
     '*',
     '_',
     '{',
     '}',
     '[',
     ']',
     '(',
     ')',
     '>',
     '#',
     '+',
     '-',
     '.',
     '!']

    def __init__(self, *args, **kwargs):
        pos = ['extensions',
         'extension_configs',
         'safe_mode',
         'output_format']
        c = 0
        for arg in args:
            if not kwargs.has_key(pos[c]):
                kwargs[pos[c]] = arg
            c += 1
            if c == len(pos):
                break

        for option, default in self.option_defaults.items():
            setattr(self, option, kwargs.get(option, default))

        self.safeMode = kwargs.get('safe_mode', False)
        if self.safeMode and not kwargs.has_key('enable_attributes'):
            self.enable_attributes = False
        self.registeredExtensions = []
        self.docType = ''
        self.stripTopLevelTags = True
        self.build_parser()
        self.references = {}
        self.htmlStash = util.HtmlStash()
        self.registerExtensions(extensions=kwargs.get('extensions', []), configs=kwargs.get('extension_configs', {}))
        self.set_output_format(kwargs.get('output_format', 'xhtml1'))
        self.reset()

    def build_parser(self):
        self.preprocessors = build_preprocessors(self)
        self.parser = build_block_parser(self)
        self.inlinePatterns = build_inlinepatterns(self)
        self.treeprocessors = build_treeprocessors(self)
        self.postprocessors = build_postprocessors(self)
        return self

    def registerExtensions(self, extensions, configs):
        for ext in extensions:
            if isinstance(ext, basestring):
                ext = self.build_extension(ext, configs.get(ext, []))
            if isinstance(ext, Extension):
                ext.extendMarkdown(self, globals())
            elif ext is not None:
                raise TypeError('Extension "%s.%s" must be of type: "markdown.Extension"' % (ext.__class__.__module__, ext.__class__.__name__))

        return self

    def build_extension(self, ext_name, configs = []):
        configs = dict(configs)
        pos = ext_name.find('(')
        if pos > 0:
            ext_args = ext_name[pos + 1:-1]
            ext_name = ext_name[:pos]
            pairs = [ x.split('=') for x in ext_args.split(',') ]
            configs.update([ (x.strip(), y.strip()) for x, y in pairs ])
        module_name = ext_name
        if '.' not in ext_name:
            module_name = '.'.join(['markdown.extensions', ext_name])
        try:
            module = __import__(module_name, {}, {}, [module_name.rpartition('.')[0]])
        except ImportError:
            module_name_old_style = '_'.join(['mdx', ext_name])
            try:
                module = __import__(module_name_old_style)
            except ImportError as e:
                message = "Failed loading extension '%s' from '%s' or '%s'" % (ext_name, module_name, module_name_old_style)
                e.args = (message,) + e.args[1:]
                raise

        try:
            return module.makeExtension(configs.items())
        except AttributeError as e:
            message = e.args[0]
            message = "Failed to initiate extension '%s': %s" % (ext_name, message)
            e.args = (message,) + e.args[1:]
            raise

    def registerExtension(self, extension):
        self.registeredExtensions.append(extension)
        return self

    def reset(self):
        self.htmlStash.reset()
        self.references.clear()
        for extension in self.registeredExtensions:
            if hasattr(extension, 'reset'):
                extension.reset()

        return self

    def set_output_format(self, format):
        self.output_format = format.lower()
        try:
            self.serializer = self.output_formats[self.output_format]
        except KeyError as e:
            valid_formats = self.output_formats.keys()
            valid_formats.sort()
            message = 'Invalid Output Format: "%s". Use one of %s.' % (self.output_format, '"' + '", "'.join(valid_formats) + '"')
            e.args = (message,) + e.args[1:]
            raise

        return self

    def convert(self, source):
        if not source.strip():
            return u''
        try:
            source = unicode(source)
        except UnicodeDecodeError as e:
            e.reason += '. -- Note: Markdown only accepts unicode input!'
            raise

        source = source.replace(util.STX, '').replace(util.ETX, '')
        source = source.replace('\r\n', '\n').replace('\r', '\n') + '\n\n'
        source = re.sub('\\n\\s+\\n', '\n\n', source)
        source = source.expandtabs(self.tab_length)
        self.lines = source.split('\n')
        for prep in self.preprocessors.values():
            self.lines = prep.run(self.lines)

        root = self.parser.parseDocument(self.lines).getroot()
        for treeprocessor in self.treeprocessors.values():
            newRoot = treeprocessor.run(root)
            if newRoot is not None:
                root = newRoot

        output = self.serializer(root)
        if self.stripTopLevelTags:
            try:
                start = output.index('<%s>' % self.doc_tag) + len(self.doc_tag) + 2
                end = output.rindex('</%s>' % self.doc_tag)
                output = output[start:end].strip()
            except ValueError:
                if output.strip().endswith('<%s />' % self.doc_tag):
                    output = ''
                else:
                    raise ValueError('Markdown failed to strip top-level tags. Document=%r' % output.strip())

        for pp in self.postprocessors.values():
            output = pp.run(output)

        return output.strip()

    def convertFile(self, input = None, output = None, encoding = None):
        encoding = encoding or 'utf-8'
        if input:
            if isinstance(input, str):
                input_file = codecs.open(input, mode='r', encoding=encoding)
            else:
                input_file = codecs.getreader(encoding)(input)
            text = input_file.read()
            input_file.close()
        else:
            text = sys.stdin.read()
            if not isinstance(text, unicode):
                text = text.decode(encoding)
        text = text.lstrip('\\ufeff')
        html = self.convert(text)
        if output:
            if isinstance(output, str):
                output_file = codecs.open(output, 'w', encoding=encoding, errors='xmlcharrefreplace')
                output_file.write(html)
                output_file.close()
            else:
                writer = codecs.getwriter(encoding)
                output_file = writer(output, errors='xmlcharrefreplace')
                output_file.write(html)
        elif sys.stdout.encoding:
            sys.stdout.write(html)
        else:
            writer = codecs.getwriter(encoding)
            stdout = writer(sys.stdout, errors='xmlcharrefreplace')
            stdout.write(html)
        return self


def markdown(text, *args, **kwargs):
    md = Markdown(*args, **kwargs)
    return md.convert(text)


def markdownFromFile(*args, **kwargs):
    pos = ['input',
     'output',
     'extensions',
     'encoding']
    c = 0
    for arg in args:
        if not kwargs.has_key(pos[c]):
            kwargs[pos[c]] = arg
        c += 1
        if c == len(pos):
            break

    md = Markdown(**kwargs)
    md.convertFile(kwargs.get('input', None), kwargs.get('output', None), kwargs.get('encoding', None))
