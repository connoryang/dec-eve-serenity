#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\parser.py
import dis, re, sys, token, tokenize
from coverage.backward import set, sorted, StringIO
from coverage.backward import open_source, range
from coverage.backward import reversed
from coverage.backward import bytes_to_ints
from coverage.bytecode import ByteCodes, CodeObjects
from coverage.misc import nice_pair, expensive, join_regex
from coverage.misc import CoverageException, NoSource, NotPython

class CodeParser(object):

    def __init__(self, text = None, filename = None, exclude = None):
        self.filename = filename or '<code>'
        self.text = text
        if not self.text:
            try:
                sourcef = open_source(self.filename)
                try:
                    self.text = sourcef.read()
                finally:
                    sourcef.close()

            except IOError:
                _, err, _ = sys.exc_info()
                raise NoSource("No source for code: '%s': %s" % (self.filename, err))

        if self.text and ord(self.text[0]) == 65279:
            self.text = self.text[1:]
        self.exclude = exclude
        self.show_tokens = False
        self.lines = self.text.split('\n')
        self.excluded = set()
        self.docstrings = set()
        self.classdefs = set()
        self.multiline = {}
        self.statement_starts = set()
        self._byte_parser = None

    def _get_byte_parser(self):
        if not self._byte_parser:
            self._byte_parser = ByteParser(text=self.text, filename=self.filename)
        return self._byte_parser

    byte_parser = property(_get_byte_parser)

    def lines_matching(self, *regexes):
        regex_c = re.compile(join_regex(regexes))
        matches = set()
        for i, ltext in enumerate(self.lines):
            if regex_c.search(ltext):
                matches.add(i + 1)

        return matches

    def _raw_parse(self):
        if self.exclude:
            self.excluded = self.lines_matching(self.exclude)
        indent = 0
        exclude_indent = 0
        excluding = False
        prev_toktype = token.INDENT
        first_line = None
        empty = True
        tokgen = tokenize.generate_tokens(StringIO(self.text).readline)
        for toktype, ttext, (slineno, _), (elineno, _), ltext in tokgen:
            if self.show_tokens:
                print '%10s %5s %-20r %r' % (tokenize.tok_name.get(toktype, toktype),
                 nice_pair((slineno, elineno)),
                 ttext,
                 ltext)
            if toktype == token.INDENT:
                indent += 1
            elif toktype == token.DEDENT:
                indent -= 1
            elif toktype == token.NAME and ttext == 'class':
                self.classdefs.add(slineno)
            elif toktype == token.OP and ttext == ':':
                if not excluding and elineno in self.excluded:
                    exclude_indent = indent
                    excluding = True
            elif toktype == token.STRING and prev_toktype == token.INDENT:
                self.docstrings.update(range(slineno, elineno + 1))
            elif toktype == token.NEWLINE:
                if first_line is not None and elineno != first_line:
                    rng = (first_line, elineno)
                    for l in range(first_line, elineno + 1):
                        self.multiline[l] = rng

                first_line = None
            if ttext.strip() and toktype != tokenize.COMMENT:
                empty = False
                if first_line is None:
                    first_line = slineno
                    if excluding and indent <= exclude_indent:
                        excluding = False
                    if excluding:
                        self.excluded.add(elineno)
            prev_toktype = toktype

        if not empty:
            self.statement_starts.update(self.byte_parser._find_statements())

    def first_line(self, line):
        rng = self.multiline.get(line)
        if rng:
            first_line = rng[0]
        else:
            first_line = line
        return first_line

    def first_lines(self, lines, ignore = None):
        ignore = ignore or []
        lset = set()
        for l in lines:
            if l in ignore:
                continue
            new_l = self.first_line(l)
            if new_l not in ignore:
                lset.add(new_l)

        return sorted(lset)

    def parse_source(self):
        try:
            self._raw_parse()
        except (tokenize.TokenError, IndentationError):
            _, tokerr, _ = sys.exc_info()
            msg, lineno = tokerr.args
            raise NotPython("Couldn't parse '%s' as Python source: '%s' at %s" % (self.filename, msg, lineno))

        excluded_lines = self.first_lines(self.excluded)
        ignore = excluded_lines + list(self.docstrings)
        lines = self.first_lines(self.statement_starts, ignore)
        return (lines, excluded_lines)

    def arcs(self):
        all_arcs = []
        for l1, l2 in self.byte_parser._all_arcs():
            fl1 = self.first_line(l1)
            fl2 = self.first_line(l2)
            if fl1 != fl2:
                all_arcs.append((fl1, fl2))

        return sorted(all_arcs)

    arcs = expensive(arcs)

    def exit_counts(self):
        excluded_lines = self.first_lines(self.excluded)
        exit_counts = {}
        for l1, l2 in self.arcs():
            if l1 < 0:
                continue
            if l1 in excluded_lines:
                continue
            if l2 in excluded_lines:
                continue
            if l1 not in exit_counts:
                exit_counts[l1] = 0
            exit_counts[l1] += 1

        for l in self.classdefs:
            if l in exit_counts:
                exit_counts[l] -= 1

        return exit_counts

    exit_counts = expensive(exit_counts)


def _opcode(name):
    return dis.opmap[name]


def _opcode_set(*names):
    s = set()
    for name in names:
        try:
            s.add(_opcode(name))
        except KeyError:
            pass

    return s


OPS_CODE_END = _opcode_set('RETURN_VALUE')
OPS_CHUNK_END = _opcode_set('JUMP_ABSOLUTE', 'JUMP_FORWARD', 'RETURN_VALUE', 'RAISE_VARARGS', 'BREAK_LOOP', 'CONTINUE_LOOP')
OPS_CHUNK_BEGIN = _opcode_set('JUMP_ABSOLUTE', 'JUMP_FORWARD')
OPS_PUSH_BLOCK = _opcode_set('SETUP_LOOP', 'SETUP_EXCEPT', 'SETUP_FINALLY', 'SETUP_WITH')
OPS_EXCEPT_BLOCKS = _opcode_set('SETUP_EXCEPT', 'SETUP_FINALLY')
OPS_POP_BLOCK = _opcode_set('POP_BLOCK')
OPS_NO_JUMP = OPS_PUSH_BLOCK
OP_BREAK_LOOP = _opcode('BREAK_LOOP')
OP_END_FINALLY = _opcode('END_FINALLY')
OP_COMPARE_OP = _opcode('COMPARE_OP')
COMPARE_EXCEPTION = 10
OP_LOAD_CONST = _opcode('LOAD_CONST')
OP_RETURN_VALUE = _opcode('RETURN_VALUE')

class ByteParser(object):

    def __init__(self, code = None, text = None, filename = None):
        if code:
            self.code = code
            self.text = text
        else:
            if not text:
                sourcef = open_source(filename)
                try:
                    text = sourcef.read()
                finally:
                    sourcef.close()

            self.text = text
            try:
                self.code = compile(text + '\n', filename, 'exec')
            except SyntaxError:
                _, synerr, _ = sys.exc_info()
                raise NotPython("Couldn't parse '%s' as Python source: '%s' at line %d" % (filename, synerr.msg, synerr.lineno))

        for attr in ['co_lnotab',
         'co_firstlineno',
         'co_consts',
         'co_code']:
            if not hasattr(self.code, attr):
                raise CoverageException("This implementation of Python doesn't support code analysis.\nRun coverage.py under CPython for this command.")

    def child_parsers(self):
        children = CodeObjects(self.code)
        return [ ByteParser(code=c, text=self.text) for c in children ]

    def _bytes_lines(self):
        byte_increments = bytes_to_ints(self.code.co_lnotab[0::2])
        line_increments = bytes_to_ints(self.code.co_lnotab[1::2])
        last_line_num = None
        line_num = self.code.co_firstlineno
        byte_num = 0
        for byte_incr, line_incr in zip(byte_increments, line_increments):
            if byte_incr:
                if line_num != last_line_num:
                    yield (byte_num, line_num)
                    last_line_num = line_num
                byte_num += byte_incr
            line_num += line_incr

        if line_num != last_line_num:
            yield (byte_num, line_num)

    def _find_statements(self):
        for bp in self.child_parsers():
            for _, l in bp._bytes_lines():
                yield l

    def _block_stack_repr(self, block_stack):
        blocks = ', '.join([ '(%s, %r)' % (dis.opname[b[0]], b[1]) for b in block_stack ])
        return '[' + blocks + ']'

    def _split_into_chunks(self):
        chunks = []
        chunk = None
        bytes_lines_map = dict(self._bytes_lines())
        block_stack = []
        ignore_branch = 0
        ult = penult = None
        jump_to = set()
        for bc in ByteCodes(self.code.co_code):
            if bc.jump_to >= 0:
                jump_to.add(bc.jump_to)

        chunk_lineno = 0
        for bc in ByteCodes(self.code.co_code):
            start_new_chunk = False
            first_chunk = False
            if bc.offset in bytes_lines_map:
                start_new_chunk = True
                chunk_lineno = bytes_lines_map[bc.offset]
                first_chunk = True
            elif bc.offset in jump_to:
                start_new_chunk = True
            elif bc.op in OPS_CHUNK_BEGIN:
                start_new_chunk = True
            if not chunk or start_new_chunk:
                if chunk:
                    chunk.exits.add(bc.offset)
                chunk = Chunk(bc.offset, chunk_lineno, first_chunk)
                chunks.append(chunk)
            if bc.jump_to >= 0 and bc.op not in OPS_NO_JUMP:
                if ignore_branch:
                    ignore_branch -= 1
                else:
                    chunk.exits.add(bc.jump_to)
            if bc.op in OPS_CODE_END:
                chunk.exits.add(-self.code.co_firstlineno)
            if bc.op in OPS_PUSH_BLOCK:
                block_stack.append((bc.op, bc.jump_to))
            if bc.op in OPS_POP_BLOCK:
                block_stack.pop()
            if bc.op in OPS_CHUNK_END:
                if bc.op == OP_BREAK_LOOP:
                    chunk.exits.add(block_stack[-1][1])
                chunk = None
            if bc.op == OP_END_FINALLY:
                for block in reversed(block_stack):
                    if block[0] in OPS_EXCEPT_BLOCKS:
                        chunk.exits.add(block[1])
                        break

            if bc.op == OP_COMPARE_OP and bc.arg == COMPARE_EXCEPTION:
                ignore_branch += 1
            penult = ult
            ult = bc

        if chunks:
            if ult and penult:
                if penult.op == OP_LOAD_CONST and ult.op == OP_RETURN_VALUE:
                    if self.code.co_consts[penult.arg] is None:
                        if chunks[-1].byte != penult.offset:
                            ex = -self.code.co_firstlineno
                            last_chunk = chunks[-1]
                            last_chunk.exits.remove(ex)
                            last_chunk.exits.add(penult.offset)
                            chunk = Chunk(penult.offset, last_chunk.line, False)
                            chunk.exits.add(ex)
                            chunks.append(chunk)
            chunks[-1].length = bc.next_offset - chunks[-1].byte
            for i in range(len(chunks) - 1):
                chunks[i].length = chunks[i + 1].byte - chunks[i].byte

        return chunks

    def validate_chunks(self, chunks):
        starts = set([ ch.byte for ch in chunks ])
        for ch in chunks:
            pass

    def _arcs(self):
        chunks = self._split_into_chunks()
        byte_chunks = dict([ (c.byte, c) for c in chunks ])
        yield (-1, byte_chunks[0].line)
        for chunk in chunks:
            if not chunk.first:
                continue
            chunks_considered = set()
            chunks_to_consider = [chunk]
            while chunks_to_consider:
                this_chunk = chunks_to_consider.pop()
                chunks_considered.add(this_chunk)
                for ex in this_chunk.exits:
                    if ex < 0:
                        yield (chunk.line, ex)
                    else:
                        next_chunk = byte_chunks[ex]
                        if next_chunk in chunks_considered:
                            continue
                        backward_jump = next_chunk.byte < this_chunk.byte
                        if next_chunk.first or backward_jump:
                            if next_chunk.line != chunk.line:
                                yield (chunk.line, next_chunk.line)
                        else:
                            chunks_to_consider.append(next_chunk)

    def _all_chunks(self):
        chunks = []
        for bp in self.child_parsers():
            chunks.extend(bp._split_into_chunks())

        return chunks

    def _all_arcs(self):
        arcs = set()
        for bp in self.child_parsers():
            arcs.update(bp._arcs())

        return arcs


class Chunk(object):

    def __init__(self, byte, line, first):
        self.byte = byte
        self.line = line
        self.first = first
        self.length = 0
        self.exits = set()

    def __repr__(self):
        if self.first:
            bang = '!'
        else:
            bang = ''
        return '<%d+%d @%d%s %r>' % (self.byte,
         self.length,
         self.line,
         bang,
         list(self.exits))
