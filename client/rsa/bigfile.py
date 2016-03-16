#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\bigfile.py
from rsa import key, common, pkcs1, varblock
from rsa._compat import byte

def encrypt_bigfile(infile, outfile, pub_key):
    if not isinstance(pub_key, key.PublicKey):
        raise TypeError('Public key required, but got %r' % pub_key)
    key_bytes = common.bit_size(pub_key.n) // 8
    blocksize = key_bytes - 11
    outfile.write(byte(varblock.VARBLOCK_VERSION))
    for block in varblock.yield_fixedblocks(infile, blocksize):
        crypto = pkcs1.encrypt(block, pub_key)
        varblock.write_varint(outfile, len(crypto))
        outfile.write(crypto)


def decrypt_bigfile(infile, outfile, priv_key):
    if not isinstance(priv_key, key.PrivateKey):
        raise TypeError('Private key required, but got %r' % priv_key)
    for block in varblock.yield_varblocks(infile):
        cleartext = pkcs1.decrypt(block, priv_key)
        outfile.write(cleartext)


__all__ = ['encrypt_bigfile', 'decrypt_bigfile']
