#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\scannerFiles\scannerToolsUIComponents.py
import weakref
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGridRow
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveFontConst
from eve.client.script.ui.control.buttons import BigButton
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.themeColored import FillThemeColored, LabelThemeColored, FrameThemeColored, SpriteThemeColored
from eve.client.script.ui.control.tooltips import ShortcutHint
from eve.client.script.ui.util.utilWindows import NamePopup
import carbonui.const as uiconst
import localization
import probescanning

class ProbeTooltipButtonBase(LayoutGridRow):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        LayoutGridRow.ApplyAttributes(self, attributes)
        self.func = attributes.func
        self.funcArgs = attributes.funcArgs
        self.highlight = FillThemeColored(bgParent=self, padding=(1, 0, 1, 0), opacity=0.25, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.highlight.display = False

    def OnClick(self, *args):
        if self.func:
            if self.funcArgs:
                self.func(*self.funcArgs)
            else:
                self.func()

    def OnMouseEnter(self, *args):
        self.highlight.display = True

    def OnMouseExit(self, *args):
        self.highlight.display = False

    def Disable(self):
        self.state = uiconst.UI_DISABLED
        self.opacity = 0.3

    def Enable(self):
        self.state = uiconst.UI_NORMAL
        self.opacity = 1.0


class FilterBox(Container):
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.label = LabelThemeColored(parent=self, state=uiconst.UI_DISABLED, fontsize=eveFontConst.EVE_MEDIUM_FONTSIZE, align=uiconst.CENTERLEFT, left=5)
        FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.25, frameConst=uiconst.FRAME_BORDER1_CORNER1)
        SpriteThemeColored(parent=self, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', pos=(5, -1, 7, 7), align=uiconst.CENTERRIGHT, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.5, state=uiconst.UI_DISABLED)
        self.SetText(attributes.text)

    def SetText(self, text):
        self.label.text = text
        self.width = self.label.textwidth + self.label.left * 2 + 12
        self.height = self.label.textheight + 2

    def OnMouseEnter(self, *args):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.5, duration=0.1)

    def OnMouseExit(self, *args):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.0, duration=0.3)

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_2


class IgnoredBox(Container):
    default_align = uiconst.TOPLEFT
    noIgnored = 0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.scanSvc = sm.GetService('scanSvc')
        self.label = LabelThemeColored(parent=self, state=uiconst.UI_DISABLED, fontsize=eveFontConst.EVE_MEDIUM_FONTSIZE, align=uiconst.CENTERLEFT, left=5)
        FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.25, frameConst=uiconst.FRAME_BORDER1_CORNER1)
        self.clearIcon = SpriteThemeColored(parent=self, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', pos=(5, -1, 7, 7), align=uiconst.CENTERRIGHT, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.5, state=uiconst.UI_DISABLED)
        self.SetText(attributes.text)

    def OnClick(self):
        pass

    def UpdateIgnoredAmount(self, noIgnored):
        self.noIgnored = noIgnored
        if noIgnored:
            self.hint = localization.GetByLabel('UI/Inflight/Scanner/ResetIgnoredResults')
        else:
            self.hint = ''
        self.SetText(localization.GetByLabel('UI/Inflight/Scanner/Ignored', noIgnored=noIgnored))

    def SetText(self, text):
        self.label.text = text
        self.width = self.label.textwidth + self.label.left * 2 + 12
        self.height = self.label.textheight + 2

    def OnMouseEnter(self, *args):
        if self.noIgnored:
            uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.5, duration=0.1)

    def OnMouseExit(self, *args):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.0, duration=0.3)

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_2


class ProbeTooltipButtonRow(ProbeTooltipButtonBase):

    def ApplyAttributes(self, attributes):
        ProbeTooltipButtonBase.ApplyAttributes(self, attributes)
        width = attributes.width or 128
        icon = SpriteThemeColored(texturePath=attributes.texturePath, pos=(0, 0, 17, 17), align=uiconst.CENTER, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, state=uiconst.UI_DISABLED)
        self.AddCell(icon, cellPadding=(5, 3, 4, 3))
        self.label = EveLabelSmall(text=attributes.text, bold=True, align=uiconst.CENTERLEFT, autoFitToText=True, width=width)
        self.AddCell(self.label, colSpan=self.columns - 1, cellPadding=(0, 2, 10, 2))


class ProbeTooltipCheckboxRow(ProbeTooltipButtonBase):
    deleteFunction = None
    editFunction = None

    def ApplyAttributes(self, attributes):
        ProbeTooltipButtonBase.ApplyAttributes(self, attributes)
        self.checkBox = Checkbox(groupname=attributes.groupName, align=uiconst.CENTER, checked=attributes.checked, retval=attributes.retval, wrapLabel=True, prefstype=None, width=16, height=16, state=uiconst.UI_DISABLED)
        self.AddCell(self.checkBox, cellPadding=(5, 1, 4, 1))
        self.deleteFunction = attributes.deleteFunc
        self.editFunction = attributes.editFunc
        self.label = EveLabelSmall(text=attributes.text, bold=True, align=uiconst.CENTERLEFT, autoFitToText=True, width=128)
        self.AddCell(self.label, colSpan=1 if attributes.filterIndex is not None else 2, cellPadding=(0, 2, 6, 2))
        if attributes.filterIndex is not None:
            shortcutObj = ShortcutHint(text=str(attributes.filterIndex))
            self.AddCell(shortcutObj, cellPadding=(2, 2, 2, 0))
            return shortcutObj

    def OnDelete(self, *args):
        if self.deleteFunction:
            self.state = uiconst.UI_DISABLED
            if callable(self.deleteFunction):
                self.deleteFunction()
            elif isinstance(self.deleteFunction, tuple):
                func, args = self.deleteFunction
                func(*args)
            uicore.animations.FadeOut(self, duration=0.5, callback=self.Close)

    def OnEdit(self, *args):
        if callable(self.editFunction):
            self.editFunction()
        elif isinstance(self.editFunction, tuple):
            func, args = self.editFunction
            func(*args)

    def OnClick(self, *args):
        self.checkBox.ToggleState()
        if self.func:
            self.func(self.checkBox.data['value'], self.checkBox.GetValue())

    def GetMenu(self):
        m = []
        if self.editFunction:
            m.append((localization.GetByLabel('UI/Inventory/Filters/Edit'), self.OnEdit))
        if self.deleteFunction:
            m.append((localization.GetByLabel('UI/Common/Delete'), self.OnDelete))
        return m


class ProbeTooltipButton_CustomFormation(ProbeTooltipButtonBase):

    def ApplyAttributes(self, attributes):
        ProbeTooltipButtonBase.ApplyAttributes(self, attributes)
        self.formation = attributes.formation
        self.OnChangeCallback = attributes.OnChangeCallback
        self.AddCell()
        self.label = EveLabelSmall(parent=self, text=attributes.text, bold=True, align=uiconst.CENTERLEFT)
        deleteButton = Sprite(texturePath='res:/UI/Texture/Icons/38_16_111.png', pos=(0, 0, 16, 16), align=uiconst.CENTERRIGHT, hint=localization.GetByLabel('UI/Inflight/Scanner/DeleteFormation'))
        self.AddCell(deleteButton, cellPadding=(5, 3, 4, 3))
        deleteButton.OnClick = self.DeleteFormation

    def Close(self, *args):
        ProbeTooltipButtonBase.Close(self, *args)
        self.OnChangeCallback = None

    def OnClick(self, *args):
        probescanning.customFormations.SelectFormation(self.formation[0])
        sm.GetService('scanSvc').MoveProbesToFormation(self.formation[0])
        if self.OnChangeCallback:
            self.OnChangeCallback()

    def DeleteFormation(self, *args):
        formation = self.formation
        probescanning.customFormations.DeleteFormation(formation[0])
        self.state = uiconst.UI_DISABLED
        uicore.animations.FadeOut(self, duration=0.5, callback=self.Close)
        if self.OnChangeCallback:
            self.OnChangeCallback()


class ProbeTooltipButton_SaveFormation(ProbeTooltipButtonRow):

    def ApplyAttributes(self, attributes):
        ProbeTooltipButtonRow.ApplyAttributes(self, attributes)

    def OnClick(self, *args):
        formationName = NamePopup(caption=localization.GetByLabel('UI/Inflight/Scanner/SaveCurrentFormation'), label=localization.GetByLabel('UI/Inflight/Scanner/FormationName'), maxLength=16)
        if formationName:
            sm.GetService('scanSvc').PersistCurrentFormation(formationName)


class FormationButton(BigButton):

    def ApplyAttributes(self, attributes):
        BigButton.ApplyAttributes(self, attributes)
        self.scanSvc = sm.GetService('scanSvc')
        self.align = uiconst.TOPLEFT
        self.height = 32
        self.width = 32
        self.Startup(32, 32, 0)
        self.sr.icon.SetTexturePath('res:/UI/Texture/classes/ProbeScanner/customFormation.png')
        self.hint = self.selectedFormationName
        self.UpdateButton()

    @property
    def selectedFormationID(self):
        return probescanning.customFormations.GetSelectedFormationID()

    @property
    def selectedFormationName(self):
        return probescanning.customFormations.GetSelectedFormationName() or localization.GetByLabel('UI/Inflight/Scanner/ProbeFormation')

    def UpdateButton(self):
        selectedFormationID = probescanning.customFormations.GetSelectedFormationID()
        if selectedFormationID is not None:
            if self.scanSvc.CanLaunchFormation(selectedFormationID):
                self.Enable()
            else:
                self.Disable()
        elif self.scanSvc.HasAvailableProbes():
            self.Enable()
        else:
            self.Disable()
        self.hint = self.selectedFormationName

    def OnClick(self, *args):
        selectedFormationID = probescanning.customFormations.GetSelectedFormationID()
        if selectedFormationID is not None:
            self.scanSvc.MoveProbesToFormation(selectedFormationID)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.Flush()
        tooltipPanel.columns = 3
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.margin = (0, 1, 0, 1)
        buttonPadding = 0
        formationsInfo = probescanning.customFormations.GetCustomFormationsInfo()
        buttonRow = tooltipPanel.AddRow(rowClass=ProbeTooltipButton_SaveFormation, text=localization.GetByLabel('UI/Inflight/Scanner/SaveCurrentFormation'), cellPadding=buttonPadding, texturePath='res:/UI/Texture/Classes/ProbeScanner/saveformationProbesIcon.png')
        if not self.scanSvc.GetActiveProbes() or len(formationsInfo) >= 10:
            buttonRow.Disable()
        selectedFormationID = probescanning.customFormations.GetSelectedFormationID()
        self.formationButtonsByID = {}
        for formationInfo in formationsInfo:
            formationID = formationInfo[0]
            isActiveFormation = formationID == selectedFormationID
            formationName = '%s (%i)' % (formationInfo[1], formationInfo[2])
            button = tooltipPanel.AddRow(rowClass=ProbeTooltipButton_CustomFormation, text=formationName, formation=formationInfo, OnChangeCallback=self.OnCustomFormationsChanged)
            if isActiveFormation:
                FillThemeColored(bgParent=button, padding=(3, 2, 3, 2), opacity=0.5, colorType=uiconst.COLORTYPE_UIHILIGHT)
            self.formationButtonsByID[formationInfo[0]] = button

        self.customFormationTooltip = weakref.ref(tooltipPanel)
        self.UpdateTooltipPanel(tooltipPanel)
        self.tooltipUpdateTimer = AutoTimer(100, self.UpdateTooltipPanel, tooltipPanel)

    def ReloadCustomFormationTooltip(self):
        if not self.customFormationTooltip or self.destroyed:
            return
        customFormationTooltip = self.customFormationTooltip()
        if customFormationTooltip is not None:
            self.LoadTooltipPanel(customFormationTooltip)

    def OnCustomFormationsChanged(self, *args):
        self.ReloadCustomFormationTooltip()
        self.UpdateButton()

    def UpdateTooltipPanel(self, tooltipPanel):
        if tooltipPanel.destroyed:
            self.tooltipUpdateTimer = None
            return
        for formationID, button in self.formationButtonsByID.iteritems():
            if button.destroyed:
                continue
            try:
                canLaunch = self.scanSvc.CanLaunchFormation(formationID)
            except KeyError:
                continue

            if canLaunch:
                button.Enable()
            else:
                button.Disable()
