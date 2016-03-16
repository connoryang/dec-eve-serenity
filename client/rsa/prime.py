#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\prime.py
__all__ = ['getprime', 'are_relatively_prime']
import rsa.randnum

def gcd(p, q):
    while q != 0:
        if p < q:
            p, q = q, p
        p, q = q, p % q

    return p


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
    f = pow(x, n >> 1, n)
    if j == f:
        return False
    return True


def randomized_primality_testing(n, k):
    for _ in range(k):
        x = rsa.randnum.randint(n - 1)
        if jacobi_witness(x, n):
            return False

    return True


def is_prime(number):
    return randomized_primality_testing(number, 6)


def getprime(nbits):
    while True:
        integer = rsa.randnum.read_random_int(nbits)
        integer |= 1
        if is_prime(integer):
            return integer


def are_relatively_prime(a, b):
    d = gcd(a, b)
    return d == 1


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
