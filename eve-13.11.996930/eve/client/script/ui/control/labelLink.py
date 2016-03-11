#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\labelLink.py
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveLabel import Label
from util import Color

class LabelLink(EveLabelMedium):
    __guid__ = 'uicls.LabelLink'

    def ApplyAttributes(self, attributes):
        Label.ApplyAttributes(self, attributes)
        self.state = uiconst.UI_NORMAL
        self.func = attributes.func
        self.bold = True

    def OnClick(self, *args):
        apply(self.func[0], self.func[1:])

    def OnMouseEnter(self, *args):
        self.color = Color.YELLOW

    def OnMouseExit(self, *args):
        self.color = (1.0, 1.0, 1.0, 1.0)
