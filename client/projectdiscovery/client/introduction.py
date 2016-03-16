#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\introduction.py
import uiprimitives
import uicontrols
import carbonui.const as uiconst
import localization
import const

class IntroductionScreen(uicontrols.Window):
    __guid__ = 'ProjectDiscoveryIntroduction'
    default_fixedHeight = 200
    default_fixedWidth = 400
    default_isStackable = False

    def ApplyAttributes(self, attributes):
        super(IntroductionScreen, self).ApplyAttributes(attributes)
        caption = localization.GetByLabel('UI/ProjectDiscovery/IntroductionTextWindowCaption')
        self.SetCaption(caption)
        self.SetupLayout()

    def SetupLayout(self):
        self.SetTopparentHeight(0)
        main = self.GetMainArea()
        main.padding = 5
        main_container = uiprimitives.Container(parent=main)
        text_container = uiprimitives.Container(parent=main_container, height=120, width=250, align=uiconst.TOPRIGHT)
        uicontrols.EditPlainTextCore(parent=text_container, readonly=True, height=128, setvalue=localization.GetByLabel('UI/ProjectDiscovery/IntroductionText'))
        avatar_container = uiprimitives.Container(parent=main_container, height=128, width=128, align=uiconst.TOPLEFT)
        uiprimitives.Sprite(parent=avatar_container, name='SOE_Logo', align=uiconst.TOTOP, height=128, texturePath='res:/ui/texture/corps/14_128_1.png', ignoreSize=True)
        bottom_container = uiprimitives.Container(parent=main_container, height=35, align=uiconst.TOBOTTOM)
        self.close_button = uicontrols.Button(parent=bottom_container, label=localization.GetByLabel('UI/ProjectDiscovery/IntroductionTextContinueButton'), align=uiconst.CENTER, padLeft=20, fixedwidth=100, fixedheight=25, func=lambda x: self.continue_and_check_preference())
        self.checkbox = uicontrols.Checkbox(parent=bottom_container, align=uiconst.CENTERLEFT, padLeft=10)
        self.checkbox.SetLabelText(localization.GetByLabel('UI/ProjectDiscovery/IntroductionScreenCheckboxText'))
        self.checkbox.SetSize(140, 20)

    def continue_and_check_preference(self):
        if self.checkbox.checked:
            settings.char.ui.Set(const.Settings.ProjectDiscoveryIntroductionShown, True)
        else:
            settings.char.ui.Set(const.Settings.ProjectDiscoveryIntroductionShown, False)
        self.CloseByUser()
