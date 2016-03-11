#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\cef\componentViews\playerComponentView.py
from carbon.common.script.cef.baseComponentView import BaseComponentView

class PlayerComponentView(BaseComponentView):
    __guid__ = 'cef.PlayerComponentView'
    __COMPONENT_ID__ = const.cef.PLAYER_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Player'
    __COMPONENT_CODE_NAME__ = 'player'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)


PlayerComponentView.SetupInputs()
