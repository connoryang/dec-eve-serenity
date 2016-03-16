#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\_version133.py
__author__ = 'Sybren Stuvel, Marloes de Boer and Ivo Tamboer'
__date__ = '2010-02-05'
__version__ = '1.3.3'
from cPickle import dumps, loads
import base64
import math
import os
import random
import sys
import types
import zlib
from rsa._compat import byte
import warnings
warnings.warn('Insecure version of the RSA module is imported as %s, be careful' % __name__)

def gcd(p, q):
    if p < q:
        return gcd(q, p)
    if q == 0:
        return p
    return gcd(q, abs(p % q))


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


def fast_exponentiation(a, p, n):
    result = a % n
    remainders = []
    while p != 1:
        remainders.append(p & 1)
        p = p >> 1

    while remainders:
        rem = remainders.pop()
        result = a ** rem * result ** 2 % n

    return result


def read_random_int(nbits):
    nbytes = ceil(nbits / 8.0)
    randomdata = os.urandom(nbytes)
    return bytes2int(randomdata)


def ceil(x):
    return int(math.ceil(x))


def randint(minvalue, maxvalue):
    min_nbits = 32
    range = maxvalue - minvalue
    rangebytes = ceil(math.log(range, 2) / 8.0)
    rangebits = max(rangebytes * 8, min_nbits * 2)
    nbits = random.randint(min_nbits, rangebits)
    return read_random_int(nbits) % range + minvalue


def fermat_little_theorem(p):
    a = randint(1, p - 1)
    return fast_exponentiation(a, p - 1, p)


def jacobi(a, b):
    if a % b == 0:
        return 0
    result = 1
    while a > 1:
        if a & 1:
            if (a - 1) * (b - 1) >> 2 & 1:
                result = -result
            b, a = a, b % a
        else:
            if b ** 2 - 1 >> 3 & 1:
                result = -result
            a = a >> 1

    return result


def jacobi_witness(x, n):
    j = jacobi(x, n) % n
    f = fast_exponentiation(x, (n - 1) / 2, n)
    if j == f:
        return False
    return True


def randomized_primality_testing(n, k):
    q = 0.5
    t = ceil(k / math.log(1 / q, 2))
    for i in range(t + 1):
        x = randint(1, n - 1)
        if jacobi_witness(x, n):
            return False

    return True


def is_prime(number):
    if randomized_primality_testing(number, 5):
        return True
    return False


def getprime(nbits):
    nbytes = int(math.ceil(nbits / 8.0))
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
    p = getprime(nbits)
    while True:
        q = getprime(nbits)
        if not q == p:
            break

    return (p, q)


def extended_euclid_gcd(a, b):
    if b == 0:
        return (a, 1, 0)
    q = abs(a % b)
    r = long(a / b)
    d, k, l = extended_euclid_gcd(b, q)
    return (d, l, k - l * r)


def calculate_keys(p, q, nbits):
    n = p * q
    phi_n = (p - 1) * (q - 1)
    while True:
        e = getprime(max(8, nbits / 2))
        if are_relatively_prime(e, n) and are_relatively_prime(e, phi_n):
            break

    d, i, j = extended_euclid_gcd(e, phi_n)
    if not d == 1:
        raise Exception('e (%d) and phi_n (%d) are not relatively prime' % (e, phi_n))
    if not e * i % phi_n == 1:
        raise Exception('e (%d) and i (%d) are not mult. inv. modulo phi_n (%d)' % (e, i, phi_n))
    return (e, i)


def gen_keys(nbits):
    while True:
        p, q = find_p_q(nbits)
        e, d = calculate_keys(p, q, nbits)
        if d > 0:
            break

    return (p,
     q,
     e,
     d)


def gen_pubpriv_keys(nbits):
    p, q, e, d = gen_keys(nbits)
    return ({'e': e,
      'n': p * q}, {'d': d,
      'p': p,
      'q': q})


def encrypt_int(message, ekey, n):
    if type(message) is types.IntType:
        return encrypt_int(long(message), ekey, n)
    if type(message) is not types.LongType:
        raise TypeError('You must pass a long or an int')
    if message > 0 and math.floor(math.log(message, 2)) > math.floor(math.log(n, 2)):
        raise OverflowError('The message is too long')
    return fast_exponentiation(message, ekey, n)


def decrypt_int(cyphertext, dkey, n):
    return encrypt_int(cyphertext, dkey, n)


def sign_int(message, dkey, n):
    return decrypt_int(message, dkey, n)


def verify_int(signed, ekey, n):
    return encrypt_int(signed, ekey, n)


def picklechops(chops):
    value = zlib.compress(dumps(chops))
    encoded = base64.encodestring(value)
    return encoded.strip()


def unpicklechops(string):
    return loads(zlib.decompress(base64.decodestring(string)))


def chopstring(message, key, n, funcref):
    msglen = len(message)
    mbits = msglen * 8
    nbits = int(math.floor(math.log(n, 2)))
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

    return picklechops(cypher)


def gluechops(chops, key, n, funcref):
    message = ''
    chops = unpicklechops(chops)
    for cpart in chops:
        mpart = funcref(cpart, key, n)
        message += int2bytes(mpart)

    return message


def encrypt(message, key):
    return chopstring(message, key['e'], key['n'], encrypt_int)


def sign(message, key):
    return chopstring(message, key['d'], key['p'] * key['q'], decrypt_int)


def decrypt(cypher, key):
    return gluechops(cypher, key['d'], key['p'] * key['q'], decrypt_int)


def verify(cypher, key):
    return gluechops(cypher, key['e'], key['n'], encrypt_int)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
__all__ = ['gen_pubpriv_keys',
 'encrypt',
 'decrypt',
 'sign',
 'verify']
