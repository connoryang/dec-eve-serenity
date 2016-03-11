#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\util\utilWindows.py


def NamePopup(caption = None, label = None, setvalue = '', maxLength = None, passwordChar = None, validator = None):
    from eve.client.script.ui.util.namedPopup import NamePopupWnd
    wnd = NamePopupWnd.Open(caption=caption, label=label, setvalue=setvalue, maxLength=maxLength, passwordChar=passwordChar, validator=validator)
    if wnd.ShowModal() == 1:
        return wnd.result


exports = {'uiutil.NamePopup': NamePopup}
