#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\util\linkUtil.py
from carbonui.util.stringManip import GetAsUnicode

def GetShowInfoLink(typeID, text, itemID = None):
    if itemID:
        return '<a href="showinfo:%s//%s">%s</a>' % (typeID, itemID, text)
    else:
        return '<a href="showinfo:%s">%s</a>' % (typeID, text)


def IsLink(text):
    textAsUnicode = GetAsUnicode(text)
    if textAsUnicode.find('<url') != -1:
        return True
    if textAsUnicode.find('<a href') != -1:
        return True
    return False
