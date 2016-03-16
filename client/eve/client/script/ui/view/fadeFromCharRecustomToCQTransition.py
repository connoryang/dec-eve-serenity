#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\fadeFromCharRecustomToCQTransition.py
from eve.client.script.ui.view.fadeToCQTransition import FadeToCQTransition

class FadeFromCharRecustomToCQTransition(FadeToCQTransition):
    __guid__ = 'viewstate.FadeFromCharRecustomToCQTransition'

    def __init__(self, fadeTimeMS = 1000, fadeInTimeMS = None, fadeOutTimeMS = None, **kwargs):
        FadeToCQTransition.__init__(self, **kwargs)
        self.allowReopen = False
