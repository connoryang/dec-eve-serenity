#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\core.py
from rsa._compat import is_integer

def assert_int(var, name):
    if is_integer(var):
        return
    raise TypeError('%s should be an integer, not %s' % (name, var.__class__))


def encrypt_int(message, ekey, n):
    assert_int(message, 'message')
    assert_int(ekey, 'ekey')
    assert_int(n, 'n')
    if message < 0:
        raise ValueError('Only non-negative numbers are supported')
    if message > n:
        raise OverflowError('The message %i is too long for n=%i' % (message, n))
    return pow(message, ekey, n)


def decrypt_int(cyphertext, dkey, n):
    assert_int(cyphertext, 'cyphertext')
    assert_int(dkey, 'dkey')
    assert_int(n, 'n')
    message = pow(cyphertext, dkey, n)
    return message
