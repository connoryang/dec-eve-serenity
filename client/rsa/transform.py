#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\transform.py
from __future__ import absolute_import
try:
    import psyco
    psyco.full()
except ImportError:
    pass

import binascii
from struct import pack
from rsa import common
from rsa._compat import is_integer, b, byte, get_word_alignment, ZERO_BYTE, EMPTY_BYTE

def bytes2int(raw_bytes):
    return int(binascii.hexlify(raw_bytes), 16)


def _int2bytes(number, block_size = None):
    if not is_integer(number):
        raise TypeError("You must pass an integer for 'number', not %s" % number.__class__)
    if number < 0:
        raise ValueError('Negative numbers cannot be used: %i' % number)
    if number == 0:
        needed_bytes = 1
        raw_bytes = [ZERO_BYTE]
    else:
        needed_bytes = common.byte_size(number)
        raw_bytes = []
    if block_size and block_size > 0:
        if needed_bytes > block_size:
            raise OverflowError('Needed %i bytes for number, but block size is %i' % (needed_bytes, block_size))
    while number > 0:
        raw_bytes.insert(0, byte(number & 255))
        number >>= 8

    if block_size and block_size > 0:
        padding = (block_size - needed_bytes) * ZERO_BYTE
    else:
        padding = EMPTY_BYTE
    return padding + EMPTY_BYTE.join(raw_bytes)


def bytes_leading(raw_bytes, needle = ZERO_BYTE):
    leading = 0
    _byte = needle[0]
    for x in raw_bytes:
        if x == _byte:
            leading += 1
        else:
            break

    return leading


def int2bytes(number, fill_size = None, chunk_size = None, overflow = False):
    if number < 0:
        raise ValueError('Number must be an unsigned integer: %d' % number)
    if fill_size and chunk_size:
        raise ValueError('You can either fill or pad chunks, but not both')
    number & 1
    raw_bytes = b('')
    num = number
    word_bits, _, max_uint, pack_type = get_word_alignment(num)
    pack_format = '>%s' % pack_type
    while num > 0:
        raw_bytes = pack(pack_format, num & max_uint) + raw_bytes
        num >>= word_bits

    zero_leading = bytes_leading(raw_bytes)
    if number == 0:
        raw_bytes = ZERO_BYTE
    raw_bytes = raw_bytes[zero_leading:]
    length = len(raw_bytes)
    if fill_size and fill_size > 0:
        if not overflow and length > fill_size:
            raise OverflowError('Need %d bytes for number, but fill size is %d' % (length, fill_size))
        raw_bytes = raw_bytes.rjust(fill_size, ZERO_BYTE)
    elif chunk_size and chunk_size > 0:
        remainder = length % chunk_size
        if remainder:
            padding_size = chunk_size - remainder
            raw_bytes = raw_bytes.rjust(length + padding_size, ZERO_BYTE)
    return raw_bytes


if __name__ == '__main__':
    import doctest
    doctest.testmod()
