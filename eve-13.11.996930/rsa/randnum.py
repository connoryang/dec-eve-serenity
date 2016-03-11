#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\randnum.py
import os
from rsa import common, transform
from rsa._compat import byte

def read_random_bits(nbits):
    nbytes, rbits = divmod(nbits, 8)
    randomdata = os.urandom(nbytes)
    if rbits > 0:
        randomvalue = ord(os.urandom(1))
        randomvalue >>= 8 - rbits
        randomdata = byte(randomvalue) + randomdata
    return randomdata


def read_random_int(nbits):
    randomdata = read_random_bits(nbits)
    value = transform.bytes2int(randomdata)
    value |= 1 << nbits - 1
    return value


def randint(maxvalue):
    bit_size = common.bit_size(maxvalue)
    tries = 0
    while True:
        value = read_random_int(bit_size)
        if value <= maxvalue:
            break
        if tries and tries % 10 == 0:
            bit_size -= 1
        tries += 1

    return value
