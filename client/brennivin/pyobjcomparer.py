#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\pyobjcomparer.py
from pprint import pformat as _pformat
from . import compat as _compat
TOLERANCE = 0.0001

def _check_type(b, type_, breadcrumb):
    if not isinstance(b, type_):
        breadcrumb.append('%s is not a %s' % (type(b).__name__, type_.__name__))
        return False
    return True


def _compare_default(a, b, breadcrumb):
    if a != b:
        breadcrumb.append('%r != %r' % (a, b))
        return False
    return True


def _compare_number(a, b, breadcrumb):
    if abs(a - b) >= TOLERANCE:
        breadcrumb.append('%r != %r' % (a, b))
        return False
    return True


def _compare_set(a, b, breadcrumb):
    if not _check_type(b, set, breadcrumb):
        return False
    a = sorted(a)
    b = sorted(b)
    return _compare(a, b, breadcrumb)


def _compare_tuple(a, b, breadcrumb):
    if not _check_type(b, tuple, breadcrumb):
        return False
    return _compare(list(a), list(b), breadcrumb)


def _compare_list(a, b, breadcrumb):
    if not _check_type(b, list, breadcrumb):
        return False
    if len(a) != len(b):
        breadcrumb.append('len neq (%s != %s)' % (len(a), len(b)))
        return False
    for i, (aitem, bitem) in enumerate(zip(a, b)):
        eq = _compare(aitem, bitem, breadcrumb)
        if not eq:
            breadcrumb.append(i)
            return False

    return True


def _compare_dict(a, b, breadcrumb):
    if not _check_type(b, dict, breadcrumb):
        return False
    sorted_a_keys = sorted(a.keys())
    sorted_b_keys = sorted(b.keys())
    eq = _compare(sorted_a_keys, sorted_b_keys, breadcrumb)
    if not eq:
        return False
    for akey, bkey in zip(sorted_a_keys, sorted_b_keys):
        aval = a[akey]
        bval = b[bkey]
        eq = _compare(aval, bval, breadcrumb)
        if not eq:
            breadcrumb.append(akey)
            return False

    return True


MAP = {int: _compare_number,
 str: _compare_default,
 _compat.long: _compare_number,
 set: _compare_set,
 list: _compare_list,
 tuple: _compare_tuple,
 dict: _compare_dict,
 float: _compare_number,
 object: _compare_default}

def compare(a, b):
    return _compare(a, b, [])


def _compare(a, b, breadcrumb):
    comparer_func = MAP.get(type(a), _compare_default)
    eq = comparer_func(a, b, breadcrumb)
    return eq


def get_compound_diff(a, b):
    crumbs = []
    eq = _compare(a, b, crumbs)
    crumbs.reverse()
    if not eq and not crumbs:
        return [a, b]
    return crumbs


def assert_compare(a, b, print_objs = True):
    path = get_compound_diff(a, b)
    if path:
        contents = ['Value at path %s does not match.' % path]
        if print_objs:
            contents.append('a: %s' % _pformat(a))
            contents.append('b: %s' % _pformat(b))
        raise AssertionError('\n'.join(contents))
