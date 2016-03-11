#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\Alliances\all_ui_systems.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import NiceFilter
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.entries import Generic
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelSmall, EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
import carbonui.const as uiconst
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.common.lib.appConst import corpRoleDirector
import gametime
from inventorycommon.util import IsNPC
import listentry
from localization import GetByLabel
import log
from sovDashboard.claimedSystems import ClaimedSystemsDashboard
from utillib import KeyVal

class FormAlliancesSystems(Container):

    def CreateWindow(self):
        self.capitalSystemInfo = sm.GetService('alliance').GetCapitalSystemInfo()
        self.systems = sm.RemoteSvc('stationSvc').GetSystemsForAlliance(session.allianceid)
        alliance = sm.GetService('alliance').GetAlliance()
        self.isExecDirector = self._IsDirectorInExecCorp(alliance.executorCorpID)
        infoCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         0))
        topCont = Container(parent=infoCont, height=42, align=uiconst.TOTOP)
        FillThemeColored(parent=topCont, colorType=uiconst.COLORTYPE_UIHEADER, opacity=0.15)
        texturePath = 'res:/ui/Texture/classes/Sov/capitalSystem.png'
        Sprite(name='capitalIcon', parent=topCont, texturePath=texturePath, width=32, height=32, align=uiconst.CENTERLEFT, left=4)
        EveLabelLarge(text=GetByLabel('UI/Sovereignty/AllianceCapital'), parent=topCont, align=uiconst.CENTERLEFT, left=42, top=-8)
        EveLabelSmall(text=GetByLabel('UI/Sovereignty/SelectCapitalSystemDescription'), parent=topCont, align=uiconst.CENTERLEFT, left=42, top=8)
        currentSystemCont = Container(parent=infoCont, height=24, align=uiconst.TOTOP)
        self.currentCapitalLabel = EveLabelMedium(text='', left=4, parent=currentSystemCont, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        self.capitalLabel = EveLabelMedium(text=GetByLabel('UI/Sovereignty/CurrentCapital'), left=22, parent=currentSystemCont, align=uiconst.CENTERRIGHT)
        self.capitalSprite = Sprite(name='capitalIcon', parent=currentSystemCont, texturePath='res:/ui/Texture/classes/Sov/CapitalStarSelection.png', width=16, height=16, align=uiconst.CENTERRIGHT, left=4)
        self.SetDisplayOfCapitalLabelAndIcon(False)
        self.futureSystemCont = Container(parent=infoCont, height=24, align=uiconst.TOTOP)
        self.futureSystemLabel = EveLabelMedium(text='', left=4, parent=self.futureSystemCont, align=uiconst.CENTERLEFT)
        self.futureSystemTime = EveLabelMedium(text='', left=4, parent=self.futureSystemCont, align=uiconst.CENTERRIGHT)
        self.removeBtn = ButtonIcon(texturePath='res:/UI/Texture/Icons/73_16_210.png', pos=(4, 0, 16, 16), align=uiconst.CENTERRIGHT, parent=self.futureSystemCont, idx=0, func=self.RemoveCapital, hint=GetByLabel('UI/Common/Buttons/Cancel'))
        self.removeBtn.display = False
        if self.isExecDirector:
            self.removeBtn.display = True
            self.futureSystemTime.left = 22
        self.futureSystemCont.display = False
        self.claimedSystems = ClaimedSystemsDashboard(parent=self, padTop=const.defaultPadding)
        self.claimedSystems.CreateWindow()
        self.UpdateCapitalInfo()

    def UpdateCapitalInfo(self):
        self.capitalSystemInfo = sm.GetService('alliance').GetCapitalSystemInfo()
        self.UpdateCapitalText()
        self.UpdateFutureSystemText()

    def UpdateCapitalText(self):
        currentSystem = self.capitalSystemInfo.currentCapitalSystem
        if currentSystem is None:
            currentSystemText = GetByLabel('UI/Sovereignty/NoCapital')
            self.SetDisplayOfCapitalLabelAndIcon(False)
        else:
            currentSystemText = sm.GetService('infoPanel').GetSolarSystemTrace(currentSystem, '')
            self.SetDisplayOfCapitalLabelAndIcon(True)
        self.currentCapitalLabel.text = currentSystemText

    def SetDisplayOfCapitalLabelAndIcon(self, display = True):
        self.capitalLabel.display = display
        self.capitalSprite.display = display

    def UpdateFutureSystemText(self):
        if self.capitalSystemInfo.newCapitalSystem:
            self.futureSystemCont.display = True
            solarSystemID = self.capitalSystemInfo.newCapitalSystem
            self.futureSystemLabel.text = sm.GetService('infoPanel').GetSolarSystemTrace(solarSystemID, '')
            interval = max(0L, self.capitalSystemInfo.newCapitalSystemValidAfter - gametime.GetWallclockTime())
            self.futureSystemTime.text = GetByLabel('UI/Sovereignty/CapitalChangeTime', time=interval)
        else:
            self.futureSystemCont.display = False

    def _IsDirectorInExecCorp(self, executorCorpID):
        if session.allianceid is None:
            return False
        if IsNPC(session.corpid):
            return False
        if session.corpid != executorCorpID:
            return False
        if corpRoleDirector & session.corprole != corpRoleDirector:
            return False
        return True

    def RemoveCapital(self, *args):
        if eve.Message('CustomQuestion', {'header': GetByLabel('UI/Sovereignty/CancelPendingCapital'),
         'question': GetByLabel('UI/Sovereignty/CancelPendingCapitalDetails')}, uiconst.YESNO) != uiconst.ID_YES:
            return
        sm.GetService('alliance').CancelCapitalSystemTransition()
