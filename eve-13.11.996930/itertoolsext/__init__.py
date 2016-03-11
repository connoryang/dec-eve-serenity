#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\itertoolsext\__init__.py
from brennivin.itertoolsext import *

def get_column(columnid, *rows):
    if not rows:
        return
    column_elements = zip(*rows)[columnid]
    return iter(column_elements)


def get_first_matching_index(iterable, predicate):
    for i, each in enumerate(iterable):
        if predicate(each):
            return i


def dump_dic(dic, indent = 0):
    buff = []
    ind = []
    for i in xrange(0, indent):
        ind.append('\t')

    ind = ''.join(ind)
    for k, v in dic.iteritems():
        if type(v) is dict:
            buff.append('%s%s = {\n' % (ind, k))
            buff.append(dump_dic(v, indent + 1))
            buff.append('%s}\n' % ind)
        else:
            buff.append('%s%s = %s %s\n' % (ind,
             k,
             v,
             type(v)))

    return ''.join(buff)
