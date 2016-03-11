#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\loginView.py
from viewstate import View
from eve.client.script.ui.login.loginII import Login

class LoginView(View):
    __guid__ = 'viewstate.LoginView'
    __notifyevents__ = []
    __dependencies__ = []
    __layerClass__ = Login
    __progressText__ = None

    def __init__(self):
        View.__init__(self)

    def UnloadView(self):
        View.UnloadView(self)
