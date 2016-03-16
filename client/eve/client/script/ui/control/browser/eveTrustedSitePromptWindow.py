#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\browser\eveTrustedSitePromptWindow.py
import localization
import carbonui.const as uiconst
from carbonui.control.browser.trustedSitePromptWindow import TrustedSitePromptWindowCore, TrustedSitePromptWindowCoreOverride
from eve.client.script.ui.control.eveLabel import WndCaptionLabel

class TrustedSitePromptWindow(TrustedSitePromptWindowCore):
    __guid__ = 'uicls.TrustedSitePromptWindow'
    default_iconNum = 'res:/ui/Texture/WindowIcons/browser.png'

    def ApplyAttributes(self, attributes):
        TrustedSitePromptWindowCore.ApplyAttributes(self, attributes)
        self.SetWndIcon(self.iconNum)
        WndCaptionLabel(text=localization.GetByLabel('UI/Browser/TrustPrompt/Header'), parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.SetMinSize((430, 300))


TrustedSitePromptWindowCoreOverride.__bases__ = (TrustedSitePromptWindow,)
