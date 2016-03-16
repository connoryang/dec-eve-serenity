#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\varblock.py
from rsa._compat import byte, b
ZERO_BYTE = b('\x00')
VARBLOCK_VERSION = 1

def read_varint(infile):
    varint = 0
    read_bytes = 0
    while True:
        char = infile.read(1)
        if len(char) == 0:
            if read_bytes == 0:
                return (0, 0)
            raise EOFError('EOF while reading varint, value is %i so far' % varint)
        byte = ord(char)
        varint += (byte & 127) << 7 * read_bytes
        read_bytes += 1
        if not byte & 128:
            return (varint, read_bytes)


def write_varint(outfile, value):
    if value == 0:
        outfile.write(ZERO_BYTE)
        return 1
    written_bytes = 0
    while value > 0:
        to_write = value & 127
        value = value >> 7
        if value > 0:
            to_write |= 128
        outfile.write(byte(to_write))
        written_bytes += 1

    return written_bytes


def yield_varblocks(infile):
    first_char = infile.read(1)
    if len(first_char) == 0:
        raise EOFError('Unable to read VARBLOCK version number')
    version = ord(first_char)
    if version != VARBLOCK_VERSION:
        raise ValueError('VARBLOCK version %i not supported' % version)
    while True:
        block_size, read_bytes = read_varint(infile)
        if read_bytes == 0 and block_size == 0:
            break
        block = infile.read(block_size)
        read_size = len(block)
        if read_size != block_size:
            raise EOFError('Block size is %i, but could read only %i bytes' % (block_size, read_size))
        yield block


def yield_fixedblocks(infile, blocksize):
    while True:
        block = infile.read(blocksize)
        read_bytes = len(block)
        if read_bytes == 0:
            break
        yield block
        if read_bytes < blocksize:
            break
