#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\storedFittingsButtons.py
from carbonui.primitives.flowcontainer import FlowContainer, CONTENT_ALIGN_CENTER
import carbonui.const as uiconst
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.shared.export import ImportLegacyFittingsWindow
from eve.client.script.ui.shared.fittingMgmtWindow import FittingMgmt, ViewFitting
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.common.script.sys.eveCfg import GetActiveShip
from localization import GetByLabel
from utillib import KeyVal

class StoredFittingsButtons(FlowContainer):
    contentAlignment = CONTENT_ALIGN_CENTER
    contentSpacing = uiconst.BUTTONGROUPMARGIN
    default_padLeft = 6
    default_padTop = 6
    default_padRight = 6
    default_padBottom = 6

    def ApplyAttributes(self, attributes):
        FlowContainer.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.AddButton()

    def AddButton(self):
        loadFittingBtn = Button(parent=self, label=GetByLabel('UI/Fitting/FittingWindow/Browse'), func=self.LoadFittingSetup, align=uiconst.NOALIGN)
        loadFittingBtn.hint = GetByLabel('UI/Fitting/FittingWindow/BrowseTooltip')
        SetFittingTooltipInfo(targetObject=loadFittingBtn, tooltipName='BrowseSavedFittings', includeDesc=False)
        saveFittingBtn = Button(parent=self, label=GetByLabel('UI/Fitting/FittingWindow/Save'), func=self.SaveFittingSetup, align=uiconst.NOALIGN)
        saveFittingBtn.hint = GetByLabel('UI/Fitting/FittingWindow/SaveTooltip')
        SetFittingTooltipInfo(targetObject=saveFittingBtn, tooltipName='SaveFitting', includeDesc=False)
        self.stripBtn = Button(parent=self, label=GetByLabel('UI/Fitting/FittingWindow/StripFitting'), func=self.controller.StripFitting, align=uiconst.NOALIGN)
        self.stripBtn.hint = GetByLabel('UI/Fitting/FittingWindow/StripFittingTooltip')
        SetFittingTooltipInfo(targetObject=self.stripBtn, tooltipName='StripFitting', includeDesc=False)

    def LoadFittingSetup(self, *args):
        if sm.GetService('fittingSvc').HasLegacyClientFittings():
            wnd = ImportLegacyFittingsWindow.Open()
        else:
            wnd = FittingMgmt.Open()
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()

    def SaveFittingSetup(self, *args):
        fittingSvc = sm.StartService('fittingSvc')
        fitting = KeyVal()
        fitting.shipTypeID, fitting.fitData = fittingSvc.GetFittingDictForActiveShip()
        fitting.fittingID = None
        fitting.description = ''
        fitting.name = cfg.evelocations.Get(GetActiveShip()).locationName
        fitting.ownerID = 0
        windowID = 'Save_ViewFitting_%s' % GetActiveShip()
        ViewFitting.Open(windowID=windowID, fitting=fitting, truncated=None)
