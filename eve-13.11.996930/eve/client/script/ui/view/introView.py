#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\introView.py
from eve.client.script.ui.login.intro import Intro
from viewstate import View
import trinity

class IntroView(View):
    __guid__ = 'viewstate.IntroView'
    __notifyevents__ = []
    __dependencies__ = []
    __layerClass__ = Intro

    def __init__(self):
        View.__init__(self)

    def LoadView(self, **kwargs):
        pass

    def UnloadView(self):
        pass
