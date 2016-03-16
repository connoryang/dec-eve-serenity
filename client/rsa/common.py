#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\common.py


def bit_size(num):
    if num == 0:
        return 0
    if num < 0:
        num = -num
    num & 1
    hex_num = '%x' % num
    return (len(hex_num) - 1) * 4 + {'0': 0,
     '1': 1,
     '2': 2,
     '3': 2,
     '4': 3,
     '5': 3,
     '6': 3,
     '7': 3,
     '8': 4,
     '9': 4,
     'a': 4,
     'b': 4,
     'c': 4,
     'd': 4,
     'e': 4,
     'f': 4}[hex_num[0]]


def _bit_size(number):
    if number < 0:
        raise ValueError('Only nonnegative numbers possible: %s' % number)
    if number == 0:
        return 0
    bits = 0
    while number:
        bits += 1
        number >>= 1

    return bits


def byte_size(number):
    quanta, mod = divmod(bit_size(number), 8)
    if mod or number == 0:
        quanta += 1
    return quanta


def extended_gcd(a, b):
    x = 0
    y = 1
    lx = 1
    ly = 0
    oa = a
    ob = b
    while b != 0:
        q = a // b
        a, b = b, a % b
        x, lx = lx - q * x, x
        y, ly = ly - q * y, y

    if lx < 0:
        lx += ob
    if ly < 0:
        ly += oa
    return (a, lx, ly)


def inverse(x, n):
    divider, inv, _ = extended_gcd(x, n)
    if divider != 1:
        raise ValueError('x (%d) and n (%d) are not relatively prime' % (x, n))
    return inv


def crt(a_values, modulo_values):
    m = 1
    x = 0
    for modulo in modulo_values:
        m *= modulo

    for m_i, a_i in zip(modulo_values, a_values):
        M_i = m // m_i
        inv = inverse(M_i, m_i)
        x = (x + a_i * M_i * inv) % m

    return x


if __name__ == '__main__':
    import doctest
    doctest.testmod()
