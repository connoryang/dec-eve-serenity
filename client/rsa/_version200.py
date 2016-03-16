#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\_version200.py
__author__ = 'Sybren Stuvel, Marloes de Boer, Ivo Tamboer, and Barry Mead'
__date__ = '2010-02-08'
__version__ = '2.0'
import math
import os
import random
import sys
import types
from rsa._compat import byte
import warnings
warnings.warn('Insecure version of the RSA module is imported as %s' % __name__)

def bit_size(number):
    return int(math.ceil(math.log(number, 2)))


def gcd(p, q):
    while q != 0:
        if p < q:
            p, q = q, p
        p, q = q, p % q

    return p


def bytes2int(bytes):
    if not (type(bytes) is types.ListType or type(bytes) is types.StringType):
        raise TypeError('You must pass a string or a list')
    integer = 0
    for byte in bytes:
        integer *= 256
        if type(byte) is types.StringType:
            byte = ord(byte)
        integer += byte

    return integer


def int2bytes(number):
    if not (type(number) is types.LongType or type(number) is types.IntType):
        raise TypeError('You must pass a long or an int')
    string = ''
    while number > 0:
        string = '%s%s' % (byte(number & 255), string)
        number /= 256

    return string


def to64(number):
    if not (type(number) is types.LongType or type(number) is types.IntType):
        raise TypeError('You must pass a long or an int')
    if 0 <= number <= 9:
        return byte(number + 48)
    if 10 <= number <= 35:
        return byte(number + 55)
    if 36 <= number <= 61:
        return byte(number + 61)
    if number == 62:
        return byte(45)
    if number == 63:
        return byte(95)
    raise ValueError('Invalid Base64 value: %i' % number)


def from64(number):
    if not (type(number) is types.LongType or type(number) is types.IntType):
        raise TypeError('You must pass a long or an int')
    if 48 <= number <= 57:
        return number - 48
    if 65 <= number <= 90:
        return number - 55
    if 97 <= number <= 122:
        return number - 61
    if number == 45:
        return 62
    if number == 95:
        return 63
    raise ValueError('Invalid Base64 value: %i' % number)


def int2str64(number):
    if not (type(number) is types.LongType or type(number) is types.IntType):
        raise TypeError('You must pass a long or an int')
    string = ''
    while number > 0:
        string = '%s%s' % (to64(number & 63), string)
        number /= 64

    return string


def str642int(string):
    if not (type(string) is types.ListType or type(string) is types.StringType):
        raise TypeError('You must pass a string or a list')
    integer = 0
    for byte in string:
        integer *= 64
        if type(byte) is types.StringType:
            byte = ord(byte)
        integer += from64(byte)

    return integer


def read_random_int(nbits):
    nbytes = int(math.ceil(nbits / 8.0))
    randomdata = os.urandom(nbytes)
    return bytes2int(randomdata)


def randint(minvalue, maxvalue):
    min_nbits = 32
    range = maxvalue - minvalue + 1
    rangebytes = (bit_size(range) + 7) / 8
    rangebits = max(rangebytes * 8, min_nbits * 2)
    nbits = random.randint(min_nbits, rangebits)
    return read_random_int(nbits) % range + minvalue


def jacobi(a, b):
    if a == 0:
        return 0
    result = 1
    while a > 1:
        if a & 1:
            if (a - 1) * (b - 1) >> 2 & 1:
                result = -result
            a, b = b % a, a
        else:
            if b * b - 1 >> 3 & 1:
                result = -result
            a >>= 1

    if a == 0:
        return 0
    return result


def jacobi_witness(x, n):
    j = jacobi(x, n) % n
    f = pow(x, (n - 1) / 2, n)
    if j == f:
        return False
    return True


def randomized_primality_testing(n, k):
    for i in range(k):
        x = randint(1, n - 1)
        if jacobi_witness(x, n):
            return False

    return True


def is_prime(number):
    if randomized_primality_testing(number, 6):
        return True
    return False


def getprime(nbits):
    while True:
        integer = read_random_int(nbits)
        integer |= 1
        if is_prime(integer):
            break

    return integer


def are_relatively_prime(a, b):
    d = gcd(a, b)
    return d == 1


def find_p_q(nbits):
    pbits = nbits + nbits / 16
    qbits = nbits - nbits / 16
    p = getprime(pbits)
    while True:
        q = getprime(qbits)
        if not q == p:
            break

    return (p, q)


def extended_gcd(a, b):
    x = 0
    y = 1
    lx = 1
    ly = 0
    oa = a
    ob = b
    while b != 0:
        q = long(a / b)
        a, b = b, a % b
        x, lx = lx - q * x, x
        y, ly = ly - q * y, y

    if lx < 0:
        lx += ob
    if ly < 0:
        ly += oa
    return (a, lx, ly)


def calculate_keys(p, q, nbits):
    n = p * q
    phi_n = (p - 1) * (q - 1)
    while True:
        e = max(65537, getprime(nbits / 4))
        if are_relatively_prime(e, n) and are_relatively_prime(e, phi_n):
            break

    d, i, j = extended_gcd(e, phi_n)
    if not d == 1:
        raise Exception('e (%d) and phi_n (%d) are not relatively prime' % (e, phi_n))
    if i < 0:
        raise Exception("New extended_gcd shouldn't return negative values")
    if not e * i % phi_n == 1:
        raise Exception('e (%d) and i (%d) are not mult. inv. modulo phi_n (%d)' % (e, i, phi_n))
    return (e, i)


def gen_keys(nbits):
    p, q = find_p_q(nbits)
    e, d = calculate_keys(p, q, nbits)
    return (p,
     q,
     e,
     d)


def newkeys(nbits):
    nbits = max(9, nbits)
    p, q, e, d = gen_keys(nbits)
    return ({'e': e,
      'n': p * q}, {'d': d,
      'p': p,
      'q': q})


def encrypt_int(message, ekey, n):
    if type(message) is types.IntType:
        message = long(message)
    if type(message) is not types.LongType:
        raise TypeError('You must pass a long or int')
    if message < 0 or message > n:
        raise OverflowError('The message is too long')
    safebit = bit_size(n) - 2
    message += 1 << safebit
    return pow(message, ekey, n)


def decrypt_int(cyphertext, dkey, n):
    message = pow(cyphertext, dkey, n)
    safebit = bit_size(n) - 2
    message -= 1 << safebit
    return message


def encode64chops(chops):
    chips = []
    for value in chops:
        chips.append(int2str64(value))

    encoded = ','.join(chips)
    return encoded


def decode64chops(string):
    chips = string.split(',')
    chops = []
    for string in chips:
        chops.append(str642int(string))

    return chops


def chopstring(message, key, n, funcref):
    msglen = len(message)
    mbits = msglen * 8
    nbits = bit_size(n) - 2
    nbytes = nbits / 8
    blocks = msglen / nbytes
    if msglen % nbytes > 0:
        blocks += 1
    cypher = []
    for bindex in range(blocks):
        offset = bindex * nbytes
        block = message[offset:offset + nbytes]
        value = bytes2int(block)
        cypher.append(funcref(value, key, n))

    return encode64chops(cypher)


def gluechops(string, key, n, funcref):
    message = ''
    chops = decode64chops(string)
    for cpart in chops:
        mpart = funcref(cpart, key, n)
        message += int2bytes(mpart)

    return message


def encrypt(message, key):
    if 'n' not in key:
        raise Exception('You must use the public key with encrypt')
    return chopstring(message, key['e'], key['n'], encrypt_int)


def sign(message, key):
    if 'p' not in key:
        raise Exception('You must use the private key with sign')
    return chopstring(message, key['d'], key['p'] * key['q'], encrypt_int)


def decrypt(cypher, key):
    if 'p' not in key:
        raise Exception('You must use the private key with decrypt')
    return gluechops(cypher, key['d'], key['p'] * key['q'], decrypt_int)


def verify(cypher, key):
    if 'n' not in key:
        raise Exception('You must use the public key with verify')
    return gluechops(cypher, key['e'], key['n'], decrypt_int)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
__all__ = ['newkeys',
 'encrypt',
 'decrypt',
 'sign',
 'verify']
