#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\characterSelectorView.py
from viewstate import View
from eve.client.script.ui.login.charsel import CharSelection
from eve.client.script.ui.login.charSelection.characterSelection import CharacterSelection

class CharacterSelectorView(View):
    __guid__ = 'viewstate.CharacterSelectorView'
    __notifyevents__ = []
    __dependencies__ = ['menu', 'tutorial']
    __layerClass__ = CharacterSelection
    __progressText__ = 'UI_CHARSEL_ENTERINGCHARSEL'

    def LoadView(self, **kwargs):
        View.LoadView(self, **kwargs)

    def UnloadView(self):
        View.UnloadView(self)
