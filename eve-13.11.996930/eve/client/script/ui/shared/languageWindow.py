#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\languageWindow.py
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveLabel import WndCaptionLabel, EveLabelMedium
from eve.client.script.ui.control.eveWindow import Window
from localization import GetByLabel
import carbonui.const as uiconst
import localization
from localization.const import IMPORTANT_EN_OVERRIDE
from localization.util import ConvertLanguageIDToMLS
mlsToDisplayNamePaths = {'JA': 'UI/SystemMenu/Language/LanguageJapanese',
 'DE': 'UI/SystemMenu/Language/LanguageGerman',
 'EN': 'UI/SystemMenu/Language/LanguageEnglish',
 'FR': 'UI/SystemMenu/Language/LanguageFrench',
 'RU': 'UI/SystemMenu/Language/LanguageRussian',
 'ZH': 'UI/SystemMenu/Language/LanguageChinese'}

class LanguageWindow(Window):
    __guid__ = 'LanguageWindow'
    default_windowID = 'bilingualWindow'
    default_captionLabelPath = 'UI/LanguageWindow/BilingualFunctionalityHeader'
    default_iconNum = 'res:/ui/Texture/WindowIcons/Settings.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetWndIcon('res:/ui/Texture/WindowIcons/Settings.png', mainTop=-6)
        self.SetMainIconSize(64)
        self.width = 350
        self.height = 400
        self.MakeUnResizeable()
        self.currentComboValue = localization.settings.bilingualSettings.GetValue('localizationImportantNames')
        WndCaptionLabel(text=GetByLabel('UI/LanguageWindow/BilingualFunctionalityHeader'), parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.autoSizeMain = ContainerAutoSize(parent=self.sr.main, name='autoSizeMain', align=uiconst.TOTOP, callback=self.OnAutoSizeMainResize, padLeft=2, padRight=2)
        text = GetByLabel('UI/LanguageWindow/BodyText')
        EveLabelMedium(text=text, parent=self.autoSizeMain, align=uiconst.TOTOP, padding=(10, 4, 10, 0))
        self.btnGroup = ButtonGroup(parent=self.sr.main, idx=0)
        self.btnGroup.AddButton(GetByLabel('UI/Commands/Apply'), self.Save)
        self.btnGroup.AddButton(GetByLabel('UI/Common/Close'), self.Cancel)
        grid = LayoutGrid(parent=self.autoSizeMain, align=uiconst.TOTOP, columns=2, name='grid', padTop=10, padLeft=20, cellSpacing=4)
        languageID = ConvertLanguageIDToMLS(session.languageID)
        self.currentLanguageString = GetByLabel(mlsToDisplayNamePaths[languageID])
        text = GetByLabel('UI/SystemMenu/Language/Display')
        comboLabel = EveLabelMedium(text=text, parent=grid, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        comboLabel.hint = GetByLabel('UI/SystemMenu/Language/ImportantNamesExplanation')
        options = [(self.currentLanguageString, 0), (GetByLabel('UI/SystemMenu/Language/EnglishReplacement'), IMPORTANT_EN_OVERRIDE)]
        self.displayCombo = Combo(label='', parent=grid, options=options, name='displayCombo', select=self.currentComboValue, width=115, pos=(10, 0, 0, 0), align=uiconst.TOPLEFT, callback=self.OnComboChanged, hint=GetByLabel('UI/SystemMenu/Language/ImportantNamesExplanation'))
        tooltipText = self.GetTooltipCheckboxText()
        checked = localization.settings.bilingualSettings.GetValue('languageTooltip')
        self.tooltipCB = Checkbox(text=tooltipText, parent=None, configName='tooltipsCB', checked=checked, align=uiconst.TOPLEFT, width=300)
        grid.AddCell(cellObject=self.tooltipCB, colSpan=grid.columns)
        hiliteImportantText = GetByLabel('UI/SystemMenu/Language/HighlightImportantNames')
        checked = localization.settings.bilingualSettings.GetValue('localizationHighlightImportant')
        self.importantCB = Checkbox(text=hiliteImportantText, parent=None, configName='importantNamesCB', checked=checked, align=uiconst.TOPLEFT, width=300)
        grid.AddCell(cellObject=self.importantCB, colSpan=grid.columns)
        text = localization.GetByLabel('UI/LanguageWindow/ChangeSettingsInEsc')
        EveLabelMedium(text=text, parent=self.autoSizeMain, align=uiconst.TOTOP, padding=(10, 10, 10, 0))
        Line(parent=self.autoSizeMain, align=uiconst.TOTOP, color=(1, 1, 1, 0.1), padTop=4, padBottom=2)
        text = GetByLabel('UI/Messages/TxtSuppress2Body')
        self.suppressCb = Checkbox(text=text, parent=self.autoSizeMain, configName='importantNamesCB', retval=0, checked=0, align=uiconst.TOTOP, padLeft=6)

    def OnAutoSizeMainResize(self):
        headerHeight = self.GetCollapsedHeight()
        captionHeight = self.topParentHeight
        if getattr(self, 'btnGroup', None):
            buttonHeight = self.btnGroup.height
        else:
            buttonHeight = 0
        autoContainerSize = self.autoSizeMain.height + self.autoSizeMain.padTop + self.autoSizeMain.padBottom + buttonHeight
        newheight = headerHeight + captionHeight + autoContainerSize
        if newheight != self.height:
            self.height = newheight
            self.SetFixedHeight(self.height)

    def GetTooltipCheckboxText(self):
        if self.currentComboValue == localization.const.IMPORTANT_EN_OVERRIDE:
            tooltipText = GetByLabel('UI/SystemMenu/Language/ShowTooltipInLanguage', language=self.currentLanguageString)
        else:
            english = GetByLabel(mlsToDisplayNamePaths['EN'])
            tooltipText = GetByLabel('UI/SystemMenu/Language/ShowTooltipInLanguage', language=english)
        return tooltipText

    def OnComboChanged(self, combo, key, value, *args):
        self.currentComboValue = value
        tooltipText = self.GetTooltipCheckboxText()
        self.tooltipCB.SetLabel(tooltipText)

    def Save(self, *args):
        changeMade = False
        importantNamesLocalized = self.displayCombo.GetValue()
        if self.GetLanguageSetting('localizationImportantNames') != importantNamesLocalized:
            changeMade = True
            self.SetLanguageSetting('localizationImportantNames', importantNamesLocalized)
        tooltipChecked = self.tooltipCB.checked
        if self.GetLanguageSetting('languageTooltip') != tooltipChecked:
            changeMade = True
            self.SetLanguageSetting('languageTooltip', tooltipChecked)
        importantNameChecked = self.importantCB.checked
        if self.GetLanguageSetting('localizationHighlightImportant') != importantNameChecked:
            changeMade = True
            self.SetLanguageSetting('localizationHighlightImportant', importantNameChecked)
            localization.ClearImportantNameSetting()
        self.StoreSuppressSettingAndCloseWindow()
        if changeMade:
            localization.settings.bilingualSettings.UpdateAndSaveSettings()
            sm.ChainEvent('ProcessUIRefresh')
            sm.ScatterEvent('OnUIRefresh')

    def Cancel(self, *args):
        self.StoreSuppressSettingAndCloseWindow()

    def StoreSuppressSettingAndCloseWindow(self):
        suppressedChecked = self.suppressCb.checked
        if suppressedChecked:
            settings.user.suppress.Set('suppress.Bilingual_suppressMessage', True)
        self.CloseByUser()

    def GetLanguageSetting(self, configName):
        return localization.settings.bilingualSettings.GetValue(configName)

    def SetLanguageSetting(self, configName, value):
        return localization.settings.bilingualSettings.SetValue(configName, value)
