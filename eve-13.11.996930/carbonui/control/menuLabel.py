#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\control\menuLabel.py


class MenuLabel(tuple):

    def __new__(cls, text, kw = None):
        if kw is None:
            kw = {}
        return tuple.__new__(cls, (text, kw))


exports = {'uiutil.MenuLabel': MenuLabel}
