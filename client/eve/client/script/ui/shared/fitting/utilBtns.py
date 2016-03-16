#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\utilBtns.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveIcon import Icon
from localization import GetByLabel

class FittingUtilBtn(Icon):
    default_height = 16
    default_width = 16
    default_pickradius = -1
    default_idx = 0
    default_ignoreSize = True

    def ApplyAttributes(self, attributes):
        Icon.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        btnData = attributes.btnData
        self.isActive = btnData.isActive
        self.clickFunc = btnData.func
        self.mouseOverFunc = attributes.mouseOverFunc
        self.color.a = 0.0
        iconHint = btnData.hint
        if not self.isActive:
            if self.controller.GetModule() is None or self.controller.SlotExists():
                iconHint = GetByLabel('UI/Fitting/Disabled', moduleName=btnData.hint)
            else:
                iconHint = GetByLabel('UI/Fitting/CantOnlineIllegalSlot')
        self.hint = iconHint

    def OnClick(self, *args):
        if self.isActive:
            self.clickFunc(*args)

    def OnMouseEnter(self, *args):
        self.mouseOverFunc(*args)

    def SetBtnColorBasedOnIsActive(self):
        if self.isActive:
            self.color.a = 1.0
        else:
            self.color.a = 0.25

    def Hide(self):
        self.color.a = 0.0


class UtilBtnData(object):

    def __init__(self, hint, iconPath, func, isActive, onlineBtn):
        self.hint = hint
        self.iconPath = iconPath
        self.func = func
        self.isActive = isActive
        self.onlineBtn = onlineBtn
