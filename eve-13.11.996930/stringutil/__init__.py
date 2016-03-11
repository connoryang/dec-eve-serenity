#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\stringutil\__init__.py
__author__ = 'fridrik'
import sys

def strx(o):
    try:
        return str(o)
    except UnicodeEncodeError:
        sys.exc_clear()
        return unicode(o).encode('ascii', 'replace')
