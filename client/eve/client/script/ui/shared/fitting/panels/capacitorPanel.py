#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\panels\capacitorPanel.py
from carbon.common.script.util.mathUtil import DegToRad
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.util.color import Color
from dogma import const as dogmaConst
from dogma.attributes.format import GetFormatAndValue
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fitting.fittingUtil import GetShipAttribute, GetColor2, GetMultiplyColor2, FONTCOLOR_DEFAULT, FONTCOLOR_HILITE
from eve.client.script.ui.shared.fitting.panels.basePanel import BaseMenuPanel
from localization import GetByLabel
import trinity
BAD_COLOR = (70 / 256.0, 26 / 256.0, 13.0 / 256.0)
GOOD_COLOR = (240 / 256.0, 90 / 256.0, 50.0 / 256.0)
EMPTY_COLOR = (0.25, 0.25, 0.25, 0.75)

class CapacitorPanel(BaseMenuPanel):

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)
        self.capCapacityAttribute = cfg.dgmattribs.Get(dogmaConst.attributeCapacitorCapacity)
        self.rechargeRateAttribute = cfg.dgmattribs.Get(dogmaConst.attributeRechargeRate)
        self.maxcap = None

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.display = True
        self.DrawPowerCore()
        self.AddLabels()
        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def DrawPowerCore(self):
        self.powerCoreCont = Container(parent=self, name='powercore', pos=(5, 5, 30, 30), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)

    def AddLabels(self):
        self.capAndRechargeLabel = EveLabelMedium(text='', parent=self, idx=0, state=uiconst.UI_NORMAL, top=5, left=45, align=uiconst.TOPLEFT)
        self.capAndRechargeLabel.hint = GetByLabel('UI/Fitting/FittingWindow/CapacityAndRechargeRate')
        self.delteLabel = EveLabelMedium(text='', parent=self, idx=0, state=uiconst.UI_NORMAL, top=22, left=45, align=uiconst.TOPLEFT)
        self.delteLabel.hint = GetByLabel('UI/Fitting/FittingWindow/ExcessCapacitor')

    def UpdateCapacitorPanel(self, shipID, xtraCapacitor = 0.0, rechargeMultiply = 1.0, multiplyCapacitor = 1.0, reload = 0):
        peakRechargeRate, totalCapNeed, loadBalance, TTL = self.dogmaLocation.CapacitorSimulator(shipID)
        self.SetHeaderText(TTL, loadBalance)
        if not self.panelLoaded or self.powerCoreCont.destroyed:
            return
        maxcap = (xtraCapacitor + GetShipAttribute(shipID, dogmaConst.attributeCapacitorCapacity)) * multiplyCapacitor
        self.SetRechargeText(shipID, maxcap, multiplyCapacitor, rechargeMultiply, xtraCapacitor)
        self.SetDeltaText(multiplyCapacitor, peakRechargeRate, rechargeMultiply, totalCapNeed, xtraCapacitor)
        self.DrawPowercore(maxcap, loadBalance)
        self.ColorPowerCore(self.powerUnits, loadBalance, TTL)

    def SetHeaderText(self, TTL, loadBalance):
        if loadBalance > 0:
            sustainableText = '<color=0xff00ff00>'
            sustainableText += GetByLabel('UI/Fitting/FittingWindow/Stable')
            capHint = GetByLabel('UI/Fitting/FittingWindow/ModulesSustainable')
        else:
            sustainableText = '<color=0xffff0000>'
            sustainableText += GetByLabel('UI/Fitting/FittingWindow/CapacitorNotStable', time=TTL)
            capHint = GetByLabel('UI/Fitting/FittingWindow/ModulesNotSustainable')
        sustainableText += '</color>'
        self.SetStatusText(text=sustainableText.replace('<br>', ''), hintText=capHint)

    def SetRechargeText(self, shipID, maxcap, multiplyCapacitor, rechargeMultiply, xtraCapacitor):
        rechargeRate = GetShipAttribute(shipID, dogmaConst.attributeRechargeRate) * rechargeMultiply
        capText = GetByLabel('UI/Fitting/FittingWindow/CapacitorCapAndRechargeTime', capacitorCapacity=GetFormatAndValue(self.capCapacityAttribute, int(maxcap)), capacitorRechargeTime=GetFormatAndValue(self.rechargeRateAttribute, rechargeRate), startColorTag1='<color=%s>' % hex(GetColor2(xtraCapacitor, multiplyCapacitor)), startColorTag2='<color=%s>' % hex(GetMultiplyColor2(rechargeMultiply)), endColorTag='</color>')
        self.capAndRechargeLabel.text = capText

    def SetDeltaText(self, multiplyCapacitor, peakRechargeRate, rechargeMultiply, totalCapNeed, xtraCapacitor):
        sustainabilityModified = False
        if xtraCapacitor > 0 or multiplyCapacitor != 1.0 or rechargeMultiply != 1.0:
            sustainabilityModified = True
        color = FONTCOLOR_DEFAULT
        if sustainabilityModified:
            color = FONTCOLOR_HILITE
        delta = color + GetByLabel('UI/Fitting/FittingWindow/CapacitorDelta', delta=round((peakRechargeRate - totalCapNeed) * 1000, 2), percentage=round((peakRechargeRate - totalCapNeed) / peakRechargeRate * 100, 1))
        self.delteLabel.text = delta

    def DrawPowercore(self, maxcap, loadBalance):
        self.powerCoreCont.Flush()
        numcol = min(10, int(maxcap / 50))
        rotStep = 360.0 / max(1, numcol)
        colWidth = max(12, min(16, numcol and int(192 / numcol)))
        colHeight = self.powerCoreCont.height
        self.powerUnits = []
        for colIdx in xrange(numcol):
            powerColumn = self.AddPowerColumn(self.powerCoreCont, colIdx, rotStep, colWidth, colHeight)
            for cellIdx in xrange(3):
                newCell = self.AddCell(powerColumn, cellIdx)
                self.powerUnits.insert(0, newCell)

        self.maxcap = maxcap

    def AddPowerColumn(self, parent, colIdx, rotStep, colWidth, colHeight):
        rotation = DegToRad(colIdx * -rotStep)
        powerColumn = Transform(parent=parent, name='powerColumn', pos=(0,
         0,
         colWidth,
         colHeight), align=uiconst.CENTER, state=uiconst.UI_DISABLED, rotation=rotation, idx=0)
        return powerColumn

    def AddCell(self, parent, cellIdx):
        newcell = Sprite(parent=parent, name='pmark', pos=(0,
         cellIdx * 4,
         8 - cellIdx * 2,
         4), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/capacitorCell.png', color=(0.94, 0.35, 0.19, 1.0), idx=0, blendMode=trinity.TR2_SBM_ADD)
        return newcell

    def ScaleColor(self, colorTuple, scale):
        return Color(colorTuple[0] * scale, colorTuple[1] * scale, colorTuple[2] * scale)

    def ColorPowerCore(self, powerUnits, loadBalance, TTL):
        badColor = self.ScaleColor(BAD_COLOR, 1.0 - loadBalance)
        goodColor = self.ScaleColor(GOOD_COLOR, loadBalance)
        visible = max(0, min(len(powerUnits), int(loadBalance * len(powerUnits))))
        for cellIdx, each in enumerate(powerUnits):
            if cellIdx >= visible:
                each.SetRGB(*EMPTY_COLOR)
            else:
                r = badColor.r + goodColor.r
                g = badColor.g + goodColor.g
                b = badColor.b + goodColor.b
                each.SetRGB(r, g, b, 1.0)

        if loadBalance == 0:
            hint = GetByLabel('UI/Fitting/FittingWindow/CapRunsOutBy', ttl=TTL)
        else:
            hint = GetByLabel('UI/Fitting/FittingWindow/CapSustainableBy', balance=loadBalance * 100)
        self.hint = hint
