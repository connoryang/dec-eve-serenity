#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\pkcs1.py
import hashlib
import os
from rsa._compat import b
from rsa import common, transform, core, varblock
HASH_ASN1 = {'MD5': b('0 0\x0c\x06\x08*\x86H\x86\xf7\r\x02\x05\x05\x00\x04\x10'),
 'SHA-1': b('0!0\t\x06\x05+\x0e\x03\x02\x1a\x05\x00\x04\x14'),
 'SHA-256': b('010\r\x06\t`\x86H\x01e\x03\x04\x02\x01\x05\x00\x04 '),
 'SHA-384': b('0A0\r\x06\t`\x86H\x01e\x03\x04\x02\x02\x05\x00\x040'),
 'SHA-512': b('0Q0\r\x06\t`\x86H\x01e\x03\x04\x02\x03\x05\x00\x04@')}
HASH_METHODS = {'MD5': hashlib.md5,
 'SHA-1': hashlib.sha1,
 'SHA-256': hashlib.sha256,
 'SHA-384': hashlib.sha384,
 'SHA-512': hashlib.sha512}

class CryptoError(Exception):
    pass


class DecryptionError(CryptoError):
    pass


class VerificationError(CryptoError):
    pass


def _pad_for_encryption(message, target_length):
    max_msglength = target_length - 11
    msglength = len(message)
    if msglength > max_msglength:
        raise OverflowError('%i bytes needed for message, but there is only space for %i' % (msglength, max_msglength))
    padding = b('')
    padding_length = target_length - msglength - 3
    while len(padding) < padding_length:
        needed_bytes = padding_length - len(padding)
        new_padding = os.urandom(needed_bytes + 5)
        new_padding = new_padding.replace(b('\x00'), b(''))
        padding = padding + new_padding[:needed_bytes]

    return b('').join([b('\x00\x02'),
     padding,
     b('\x00'),
     message])


def _pad_for_signing(message, target_length):
    max_msglength = target_length - 11
    msglength = len(message)
    if msglength > max_msglength:
        raise OverflowError('%i bytes needed for message, but there is only space for %i' % (msglength, max_msglength))
    padding_length = target_length - msglength - 3
    return b('').join([b('\x00\x01'),
     padding_length * b('\xff'),
     b('\x00'),
     message])


def encrypt(message, pub_key):
    keylength = common.byte_size(pub_key.n)
    padded = _pad_for_encryption(message, keylength)
    payload = transform.bytes2int(padded)
    encrypted = core.encrypt_int(payload, pub_key.e, pub_key.n)
    block = transform.int2bytes(encrypted, keylength)
    return block


def decrypt(crypto, priv_key):
    blocksize = common.byte_size(priv_key.n)
    encrypted = transform.bytes2int(crypto)
    decrypted = core.decrypt_int(encrypted, priv_key.d, priv_key.n)
    cleartext = transform.int2bytes(decrypted, blocksize)
    if cleartext[0:2] != b('\x00\x02'):
        raise DecryptionError('Decryption failed')
    try:
        sep_idx = cleartext.index(b('\x00'), 2)
    except ValueError:
        raise DecryptionError('Decryption failed')

    return cleartext[sep_idx + 1:]


def sign(message, priv_key, hash):
    if hash not in HASH_ASN1:
        raise ValueError('Invalid hash method: %s' % hash)
    asn1code = HASH_ASN1[hash]
    hash = _hash(message, hash)
    cleartext = asn1code + hash
    keylength = common.byte_size(priv_key.n)
    padded = _pad_for_signing(cleartext, keylength)
    payload = transform.bytes2int(padded)
    encrypted = core.encrypt_int(payload, priv_key.d, priv_key.n)
    block = transform.int2bytes(encrypted, keylength)
    return block


def verify(message, signature, pub_key):
    blocksize = common.byte_size(pub_key.n)
    encrypted = transform.bytes2int(signature)
    decrypted = core.decrypt_int(encrypted, pub_key.e, pub_key.n)
    clearsig = transform.int2bytes(decrypted, blocksize)
    if clearsig[0:2] != b('\x00\x01'):
        raise VerificationError('Verification failed')
    try:
        sep_idx = clearsig.index(b('\x00'), 2)
    except ValueError:
        raise VerificationError('Verification failed')

    method_name, signature_hash = _find_method_hash(clearsig[sep_idx + 1:])
    message_hash = _hash(message, method_name)
    if message_hash != signature_hash:
        raise VerificationError('Verification failed')


def _hash(message, method_name):
    if method_name not in HASH_METHODS:
        raise ValueError('Invalid hash method: %s' % method_name)
    method = HASH_METHODS[method_name]
    hasher = method()
    if hasattr(message, 'read') and hasattr(message.read, '__call__'):
        for block in varblock.yield_fixedblocks(message, 1024):
            hasher.update(block)

    else:
        hasher.update(message)
    return hasher.digest()


def _find_method_hash(method_hash):
    for hashname, asn1code in HASH_ASN1.items():
        if not method_hash.startswith(asn1code):
            continue
        return (hashname, method_hash[len(asn1code):])

    raise VerificationError('Verification failed')


__all__ = ['encrypt',
 'decrypt',
 'sign',
 'verify',
 'DecryptionError',
 'VerificationError',
 'CryptoError']
if __name__ == '__main__':
    print 'Running doctests 1000x or until failure'
    import doctest
    for count in range(1000):
        failures, tests = doctest.testmod()
        if failures:
            break
        if count and count % 100 == 0:
            print '%i times' % count

    print 'Doctests done'
