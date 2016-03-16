#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\key.py
import logging
from rsa._compat import b
import rsa.prime
import rsa.pem
import rsa.common
log = logging.getLogger(__name__)

class AbstractKey(object):

    @classmethod
    def load_pkcs1(cls, keyfile, format = 'PEM'):
        methods = {'PEM': cls._load_pkcs1_pem,
         'DER': cls._load_pkcs1_der}
        if format not in methods:
            formats = ', '.join(sorted(methods.keys()))
            raise ValueError('Unsupported format: %r, try one of %s' % (format, formats))
        method = methods[format]
        return method(keyfile)

    def save_pkcs1(self, format = 'PEM'):
        methods = {'PEM': self._save_pkcs1_pem,
         'DER': self._save_pkcs1_der}
        if format not in methods:
            formats = ', '.join(sorted(methods.keys()))
            raise ValueError('Unsupported format: %r, try one of %s' % (format, formats))
        method = methods[format]
        return method()


class PublicKey(AbstractKey):
    __slots__ = ('n', 'e')

    def __init__(self, n, e):
        self.n = n
        self.e = e

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return 'PublicKey(%i, %i)' % (self.n, self.e)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, PublicKey):
            return False
        return self.n == other.n and self.e == other.e

    def __ne__(self, other):
        return not self == other

    @classmethod
    def _load_pkcs1_der(cls, keyfile):
        from pyasn1.codec.der import decoder
        priv, _ = decoder.decode(keyfile)
        as_ints = tuple((int(x) for x in priv))
        return cls(*as_ints)

    def _save_pkcs1_der(self):
        from pyasn1.type import univ, namedtype
        from pyasn1.codec.der import encoder

        class AsnPubKey(univ.Sequence):
            componentType = namedtype.NamedTypes(namedtype.NamedType('modulus', univ.Integer()), namedtype.NamedType('publicExponent', univ.Integer()))

        asn_key = AsnPubKey()
        asn_key.setComponentByName('modulus', self.n)
        asn_key.setComponentByName('publicExponent', self.e)
        return encoder.encode(asn_key)

    @classmethod
    def _load_pkcs1_pem(cls, keyfile):
        der = rsa.pem.load_pem(keyfile, 'RSA PUBLIC KEY')
        return cls._load_pkcs1_der(der)

    def _save_pkcs1_pem(self):
        der = self._save_pkcs1_der()
        return rsa.pem.save_pem(der, 'RSA PUBLIC KEY')


class PrivateKey(AbstractKey):
    __slots__ = ('n', 'e', 'd', 'p', 'q', 'exp1', 'exp2', 'coef')

    def __init__(self, n, e, d, p, q, exp1 = None, exp2 = None, coef = None):
        self.n = n
        self.e = e
        self.d = d
        self.p = p
        self.q = q
        if exp1 is None:
            self.exp1 = int(d % (p - 1))
        else:
            self.exp1 = exp1
        if exp1 is None:
            self.exp2 = int(d % (q - 1))
        else:
            self.exp2 = exp2
        if coef is None:
            self.coef = rsa.common.inverse(q, p)
        else:
            self.coef = coef

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return 'PrivateKey(%(n)i, %(e)i, %(d)i, %(p)i, %(q)i)' % self

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, PrivateKey):
            return False
        return self.n == other.n and self.e == other.e and self.d == other.d and self.p == other.p and self.q == other.q and self.exp1 == other.exp1 and self.exp2 == other.exp2 and self.coef == other.coef

    def __ne__(self, other):
        return not self == other

    @classmethod
    def _load_pkcs1_der(cls, keyfile):
        from pyasn1.codec.der import decoder
        priv, _ = decoder.decode(keyfile)
        if priv[0] != 0:
            raise ValueError('Unable to read this file, version %s != 0' % priv[0])
        as_ints = tuple((int(x) for x in priv[1:9]))
        return cls(*as_ints)

    def _save_pkcs1_der(self):
        from pyasn1.type import univ, namedtype
        from pyasn1.codec.der import encoder

        class AsnPrivKey(univ.Sequence):
            componentType = namedtype.NamedTypes(namedtype.NamedType('version', univ.Integer()), namedtype.NamedType('modulus', univ.Integer()), namedtype.NamedType('publicExponent', univ.Integer()), namedtype.NamedType('privateExponent', univ.Integer()), namedtype.NamedType('prime1', univ.Integer()), namedtype.NamedType('prime2', univ.Integer()), namedtype.NamedType('exponent1', univ.Integer()), namedtype.NamedType('exponent2', univ.Integer()), namedtype.NamedType('coefficient', univ.Integer()))

        asn_key = AsnPrivKey()
        asn_key.setComponentByName('version', 0)
        asn_key.setComponentByName('modulus', self.n)
        asn_key.setComponentByName('publicExponent', self.e)
        asn_key.setComponentByName('privateExponent', self.d)
        asn_key.setComponentByName('prime1', self.p)
        asn_key.setComponentByName('prime2', self.q)
        asn_key.setComponentByName('exponent1', self.exp1)
        asn_key.setComponentByName('exponent2', self.exp2)
        asn_key.setComponentByName('coefficient', self.coef)
        return encoder.encode(asn_key)

    @classmethod
    def _load_pkcs1_pem(cls, keyfile):
        der = rsa.pem.load_pem(keyfile, b('RSA PRIVATE KEY'))
        return cls._load_pkcs1_der(der)

    def _save_pkcs1_pem(self):
        der = self._save_pkcs1_der()
        return rsa.pem.save_pem(der, b('RSA PRIVATE KEY'))


def find_p_q(nbits, getprime_func = rsa.prime.getprime, accurate = True):
    total_bits = nbits * 2
    shift = nbits // 16
    pbits = nbits + shift
    qbits = nbits - shift
    log.debug('find_p_q(%i): Finding p', nbits)
    p = getprime_func(pbits)
    log.debug('find_p_q(%i): Finding q', nbits)
    q = getprime_func(qbits)

    def is_acceptable(p, q):
        if p == q:
            return False
        if not accurate:
            return True
        found_size = rsa.common.bit_size(p * q)
        return total_bits == found_size

    change_p = False
    while not is_acceptable(p, q):
        if change_p:
            p = getprime_func(pbits)
        else:
            q = getprime_func(qbits)
        change_p = not change_p

    return (max(p, q), min(p, q))


def calculate_keys(p, q, nbits):
    phi_n = (p - 1) * (q - 1)
    e = 65537
    try:
        d = rsa.common.inverse(e, phi_n)
    except ValueError:
        raise ValueError('e (%d) and phi_n (%d) are not relatively prime' % (e, phi_n))

    if e * d % phi_n != 1:
        raise ValueError('e (%d) and d (%d) are not mult. inv. modulo phi_n (%d)' % (e, d, phi_n))
    return (e, d)


def gen_keys(nbits, getprime_func, accurate = True):
    p, q = find_p_q(nbits // 2, getprime_func, accurate)
    e, d = calculate_keys(p, q, nbits // 2)
    return (p,
     q,
     e,
     d)


def newkeys(nbits, accurate = True, poolsize = 1):
    if nbits < 16:
        raise ValueError('Key too small')
    if poolsize < 1:
        raise ValueError('Pool size (%i) should be >= 1' % poolsize)
    if poolsize > 1:
        from rsa import parallel
        import functools
        getprime_func = functools.partial(parallel.getprime, poolsize=poolsize)
    else:
        getprime_func = rsa.prime.getprime
    p, q, e, d = gen_keys(nbits, getprime_func)
    n = p * q
    return (PublicKey(n, e), PrivateKey(n, e, d, p, q))


__all__ = ['PublicKey', 'PrivateKey', 'newkeys']
if __name__ == '__main__':
    import doctest
    try:
        for count in range(100):
            failures, tests = doctest.testmod()
            if failures:
                break
            if count and count % 10 == 0 or count == 1:
                print '%i times' % count

    except KeyboardInterrupt:
        print 'Aborted'
    else:
        print 'Doctests done'
