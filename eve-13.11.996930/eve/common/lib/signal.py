#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\lib\signal.py
import sys
if sys.platform != 'PS3':
    raise RuntimeError('This is not the proper signal module!')
