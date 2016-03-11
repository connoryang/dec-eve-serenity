#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\itertoolsext.py
import datetime as _datetime
import copy
from itertools import *
import random as _random
from . import compat as _compat
from .dochelpers import identity as _identity, default as _unsupplied
if _compat.PY3K:
    ifilter = filter
    izip = zip
    izip_longest = zip_longest

class Bundle(dict):

    def __init__(self, seq = None, **kwargs):
        dict.__init__(self, (seq or ()), **kwargs)

    def __getattr__(self, item):
        return self[item]

    def __str__(self):
        clsn = self.__class__.__name__
        return '%s(%s)' % (clsn, dict.__repr__(self))

    __repr__ = __str__

    def __deepcopy__(self, memo = None, _nil = []):
        return Bundle(copy.deepcopy(dict(self)))


class FrozenDict(dict):

    def __raise(self, *args, **kwargs):
        raise TypeError()

    clear = pop = popitem = setdefault = update = __raise
    __delitem__ = __setitem__ = __raise

    def __hash__(self):
        if not hasattr(self, '_hash'):
            self._hash = 0
            for pair in self.items():
                self._hash ^= hash(pair)

        return self._hash


def all(seq, predicate = bool):
    for item in seq:
        if not predicate(item):
            return False

    return True


def any(seq, predicate = bool):
    for item in seq:
        if predicate(item):
            return True

    return False


def bucket(seq, keyprojection = _identity, valueprojection = _identity):
    result = {}
    for item in seq:
        thisbucket = result.setdefault(keyprojection(item), [])
        thisbucket.append(valueprojection(item))

    return result


def count(seq, predicate = None):
    i = 0
    if predicate is None:
        try:
            return len(seq)
        except TypeError:
            pass

        for _ in seq:
            i += 1

    else:
        for item in seq:
            if predicate(item):
                i += 1

    return i


def datespan(startdate, enddate, delta = _datetime.timedelta(days=1)):
    if startdate < enddate:
        compare = lambda current, end: current < end
        increment = lambda current: current + delta
    else:
        compare = lambda current, end: current > end
        increment = lambda current: current - delta
    currentdate = startdate
    while compare(currentdate, enddate):
        yield currentdate
        currentdate = increment(currentdate)


def first(seq, predicate = None):
    if predicate is None:
        return next(islice(seq, 1))
    filtered = ifilter(predicate, seq)
    return next(filtered)


def first_or_default(seq, predicate = None, default = None):
    try:
        return first(seq, predicate)
    except StopIteration:
        return default


def flatmap(function, sequence):
    for item in sequence:
        subseq = function(item)
        for subitem in subseq:
            yield subitem


def groupby2(seq, keyfunc):
    sseq = sorted(seq, key=keyfunc)
    for key, group in groupby(sseq, keyfunc):
        yield (key, list(group))


def groups_of_n(seq, n):
    evenlyDivisible = len(seq) % n == 0
    if not evenlyDivisible:
        msg = 'Sequence length %s not divisible by %s' % (len(seq), n)
        raise ArithmeticError(msg)
    return [ seq[i:i + n] for i in range(0, len(seq), n) ]


def last(seq, predicate = None):
    lastitem = last_or_default(seq, predicate, _unsupplied)
    if lastitem is _unsupplied:
        raise StopIteration()
    return lastitem


def last_or_default(seq, predicate = None, default = None):
    lastitem = default
    for item in seq:
        if predicate:
            if predicate(item):
                lastitem = item
        else:
            lastitem = item

    return lastitem


def single(seq):
    iterator = iter(seq)
    try:
        result = next(iterator)
    except StopIteration:
        raise

    try:
        next(iterator)
    except StopIteration:
        return result

    raise StopIteration('Sequence has more than one item.')


def skip(sequence, number):
    cnt = 0
    for item in sequence:
        if cnt >= number:
            yield item
        else:
            cnt += 1


def take(seq, number, predicate = None):
    if not isinstance(number, (int, float, _compat.long)):
        raise TypeError('number arg must be a number type.')
    yieldedcount = 0
    for item in seq:
        if yieldedcount >= number:
            break
        if predicate is None or predicate(item):
            yield item
            yieldedcount += 1


def unique(seq, transform = _identity):
    seen = set()
    for item in seq:
        marker = transform(item)
        if marker in seen:
            continue
        seen.add(marker)
        yield item


def treeyield_depthfirst(node, getchildren, getchild = None, yieldnode = False):
    if yieldnode:
        yield node
    childEnumerator = getchildren(node)
    if getchild:
        childEnumerator = range(childEnumerator)
    for child in childEnumerator:
        if getchild:
            child = getchild(node, child)
        for grandkid in treeyield_depthfirst(child, getchildren, getchild=getchild, yieldnode=True):
            yield grandkid


def treeyield_breadthfirst(node, getchildren, getchild = None, yieldnode = False):
    if yieldnode:
        yield node
    childEnumerator = getchildren(node)
    if getchild:
        childEnumerator = range(childEnumerator)
    children = []
    for child in childEnumerator:
        if getchild:
            child = getchild(node, child)
        yield child
        children.append(child)

    for child in children:
        for grandkid in treeyield_breadthfirst(child, getchildren, getchild=getchild):
            yield grandkid


def get_compound_item(collection, *indices):
    result = collection
    for ind in indices:
        result = result[ind]

    return result


def set_compound_item(collection, value, *indices):
    operative = collection
    for ind in indices[:-1]:
        operative = operative[ind]

    operative[indices[-1]] = value


def del_compound_item(collection, *indices):
    f = get_compound_item(collection, *indices[:-1])
    del f[indices[-1]]


def _getattr_from_compound_element(obj, e):
    if isinstance(e, int):
        attr = obj[e]
    else:
        attr = getattr(obj, e)
    return attr


def get_compound_attr(obj, *namesandindices):
    currentattr = obj
    for e in namesandindices:
        currentattr = _getattr_from_compound_element(currentattr, e)

    return currentattr


def set_compound_attr(obj, value, *namesandindices):
    currentattr = obj
    for e in namesandindices[:-1]:
        currentattr = _getattr_from_compound_element(currentattr, e)

    setattr(currentattr, namesandindices[-1], value)


def dict_add(alpha, beta, adder_function = None):
    if adder_function is None:
        adder_function = lambda value_a, value_b: value_a + value_b
    for key in beta:
        if key in alpha:
            alpha[key] = adder_function(alpha[key], beta[key])
        else:
            alpha[key] = beta[key]


def shuffle(col, maxattempts = 5):
    ret = list(col)
    if not ret or len(ret) == 1:
        return ret
    attempts = 0
    while True:
        _random.shuffle(ret)
        if col != ret:
            return ret
        attempts += 1
        if attempts > maxattempts:
            raise AssertionError('Could not get a shuffle in %s attempts.' % maxattempts)


def remove_duplicates_and_preserve_order(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x)) ]
