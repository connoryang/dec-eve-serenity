#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\planet\pinContainers\ProcessorContainer.py
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import evetypes
import uiprimitives
import uicontrols
import util
import uicls
import blue
from service import ROLE_GML
import uthread
import eve.client.script.ui.control.entries as listentry
import uiutil
import localization
from .BasePinContainer import BasePinContainer, CaptionAndSubtext
from .. import planetCommon
import eve.common.script.planet.entities.basePin as basePin

class ProcessorContainer(BasePinContainer):
    __guid__ = 'planet.ui.ProcessorContainer'
    default_name = 'ProcessorContainer'
    default_width = 320
    INFO_CONT_HEIGHT = 95

    def _GetActionButtons(self):
        btns = [util.KeyVal(id=planetCommon.PANEL_SCHEMATICS, panelCallback=self.PanelShowSchematics), util.KeyVal(id=planetCommon.PANEL_PRODUCTS, panelCallback=self.PanelShowProducts)]
        btns.extend(BasePinContainer._GetActionButtons(self))
        return btns

    def PanelShowSchematics(self):
        self.schematicsCont = uiprimitives.Container(parent=self.actionCont, name='schematicsCont', align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        self.schematicsScroll = uicontrols.Scroll(parent=self.schematicsCont, name='schematicsScroll', align=uiconst.TOALL)
        self.schematicsScroll.Startup()
        self.schematicsScroll.sr.id = 'planetProcessorSchematicsScroll'
        self.schematicsScroll.multiSelect = False
        self.schematicsScroll.OnSelectionChange = self.OnSchematicScrollSelectionChange
        self.selectedSchematicCont = uiprimitives.Container(parent=self.schematicsCont, idx=0, name='selectedSchematicCont', height=138, padTop=7, align=uiconst.TOBOTTOM, state=uiconst.UI_PICKCHILDREN)
        self.LoadSchematicsScroll()
        return self.schematicsCont

    def LoadSchematicsScroll(self):
        scrolllist = []
        for schematic in planetCommon.GetSchematicData(self.pin.typeID):
            data = util.KeyVal(label=schematic.name, schematic=schematic, itemID=None, typeID=schematic.outputs[0].typeID, getIcon=True, OnClick=None, OnDblClick=self.InstallSchematic)
            sortBy = schematic.name
            scrolllist.append((sortBy, listentry.Get('Item', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        self.schematicsScroll.Load(contentList=scrolllist, headers=[])
        self.schematicsScroll.SetSelected(0)

    def OnSchematicScrollSelectionChange(self, entries):
        if not entries:
            return
        entry = entries[0]
        uicore.animations.FadeOut(self.selectedSchematicCont, duration=0.125, sleep=True)
        self.selectedSchematicCont.Flush()
        self.SubPanelSelectedSchematic(entry.schematic)
        uicore.animations.FadeIn(self.selectedSchematicCont, duration=0.125)

    def SubPanelSelectedSchematic(self, schematic):
        leftCont = uiprimitives.Container(parent=self.selectedSchematicCont, width=0.5, align=uiconst.TOLEFT_PROP, state=uiconst.UI_PICKCHILDREN)
        rightCont = uiprimitives.Container(parent=self.selectedSchematicCont, width=0.5, align=uiconst.TOLEFT_PROP, state=uiconst.UI_PICKCHILDREN)
        output = schematic.outputs[0]
        schematicTxt = localization.GetByLabel('UI/PI/Common/ItemAmount', amount=int(output.quantity), itemName=output.name)
        CaptionAndSubtext(parent=leftCont, caption=localization.GetByLabel('UI/PI/Common/OutputProduct'), subtext=schematicTxt, iconTypeID=output.typeID, left=5, top=0)
        CaptionAndSubtext(parent=leftCont, caption=localization.GetByLabel('UI/PI/Common/CycleTime'), subtext=localization.GetByLabel('UI/PI/Common/TimeHourMinSec', time=schematic.cycleTime * const.SEC), left=5, top=40)
        outputVolumeTxt = localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=schematic.outputVolume)
        CaptionAndSubtext(parent=leftCont, caption=localization.GetByLabel('UI/PI/Common/OutputPerHour'), subtext=outputVolumeTxt, left=5, top=80)
        for i, input in enumerate(schematic.inputs):
            topPos = i * 40
            caption = localization.GetByLabel('UI/PI/Common/InputNumberX', inputNum=i + 1)
            subtext = localization.GetByLabel('UI/PI/Common/ItemAmount', amount=int(input.quantity), itemName=evetypes.GetName(input.typeID))
            CaptionAndSubtext(parent=rightCont, caption=caption, subtext=subtext, iconTypeID=input.typeID, top=topPos)

        btns = [[localization.GetByLabel('UI/PI/Common/InstallSchematic'), self.InstallSchematic, ()]]
        self.buttons = uicontrols.ButtonGroup(btns=btns, idx=0, parent=self.selectedSchematicCont, line=False, alwaysLite=True)

    def InstallSchematic(self, *args):
        entries = self.schematicsScroll.GetSelected()
        if not entries:
            return
        entry = entries[0]
        schematicID = entry.schematic.schematicID
        self.planetUISvc.myPinManager.InstallSchematic(self.pin.id, schematicID)
        self.RenderIngredientGauges()
        self.ShowPanel(self.PanelShowProducts, planetCommon.PANEL_PRODUCTS)

    def _GetInfoCont(self):
        self.currProductTxt = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/Producing'))
        self.ingredientsTxt = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/SchematicInput'), top=50)
        self.ingredientsTxt.state = uiconst.UI_DISABLED
        self.ingredientCont = ContainerAutoSize(parent=self.infoContLeft, top=63, state=uiconst.UI_PICKCHILDREN)
        self.RenderIngredientGauges()
        self.currCycleGauge = uicls.Gauge(parent=self.infoContRight, value=0.0, color=planetCommon.PLANET_COLOR_CYCLE, width=140)
        self.amountPerCycleTxt = CaptionAndSubtext(parent=self.infoContRight, caption=localization.GetByLabel('UI/PI/Common/OutputPerCycle'), top=40)
        self.amountPerHourTxt = CaptionAndSubtext(parent=self.infoContRight, caption=localization.GetByLabel('UI/PI/Common/OutputPerHour'), top=70)

    def RenderIngredientGauges(self):
        self.ingredientCont.Flush()
        self.ingredientGauges = {}
        i = 0
        for typeID, amount in self.pin.GetConsumables().iteritems():
            gauge = ProcessorGaugeContainer(parent=self.ingredientCont, iconTypeID=typeID, maxAmount=amount, top=0, left=i * 24)
            self.ingredientGauges[typeID] = gauge
            i += 1

        if not self.pin.GetConsumables():
            self.ingredientsTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/NoSchematicSelected'))
        else:
            self.ingredientsTxt.SetSubtext('')

    def _UpdateInfoCont(self):
        if self.pin.schematicID:
            schematicObj = cfg.schematics.Get(self.pin.schematicID)
            schematicName = schematicObj.schematicName
            for t in cfg.schematicstypemap.get(self.pin.schematicID, []):
                if not t.isInput:
                    outputPerCycle = t.quantity
                    outputTypeID = t.typeID

            if self.pin.activityState < basePin.STATE_IDLE:
                currCycle = 0
                currCycleProportion = 0.0
                status = localization.GetByLabel('UI/Common/Inactive')
            elif self.pin.IsActive():
                nextCycle = self.pin.GetNextRunTime()
                if nextCycle is None or nextCycle < blue.os.GetWallclockTime():
                    status = localization.GetByLabel('UI/PI/Common/ProductionCompletionImminent')
                else:
                    status = localization.GetByLabel('UI/PI/Common/InProduction')
                currCycle = self.pin.GetCycleTime() - (self.pin.GetNextRunTime() - blue.os.GetWallclockTime())
                currCycleProportion = currCycle / float(self.pin.GetCycleTime())
            else:
                status = localization.GetByLabel('UI/PI/Common/WaitingForResources')
                currCycle = 0
                currCycleProportion = 0.0
        else:
            schematicName = localization.GetByLabel('UI/PI/Common/NothingExtracted')
            status = localization.GetByLabel('UI/Common/Inactive')
            currCycleProportion = 0.0
            currCycle = 0
            outputPerCycle = 0
            outputTypeID = None
        for typeID, amountNeeded in self.pin.GetConsumables().iteritems():
            amount = self.pin.GetContents().get(typeID, 0)
            gauge = self.ingredientGauges.get(typeID)
            if not gauge:
                continue
            gauge.SetValue(float(amount) / amountNeeded)
            name = evetypes.GetName(typeID)
            gauge.hint = localization.GetByLabel('UI/PI/Common/ProductionGaugeHint', resourceName=name, amount=amount, amountNeeded=amountNeeded)

        self.currProductTxt.SetSubtext(schematicName)
        if self.pin.schematicID:
            if self.pin.activityState < basePin.STATE_IDLE:
                self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
            else:
                self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CycleTimeElapsed', currTime=long(currCycle), totalTime=self.pin.GetCycleTime()))
        self.currProductTxt.SetIcon(outputTypeID)
        self.currCycleGauge.SetValueInstantly(currCycleProportion)
        self.currCycleGauge.SetText(status)
        self.amountPerCycleTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/UnitsAmount', amount=outputPerCycle))
        self.amountPerHourTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=self.pin.GetOutputVolumePerHour()))


class ProcessorGaugeContainer(uiprimitives.Container):
    __guid__ = 'planet.ui.ProcessorGauge'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_name = 'ProcessorGauge'
    default_left = 0
    default_top = 0
    default_width = 20
    default_height = 30

    def ApplyAttributes(self, attributes):
        self.uiEffects = uicls.UIEffects()
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.value = attributes.Get('value', 0.0)
        self.left = attributes.Get('left', 0)
        self.top = attributes.Get('top', 0)
        self.typeID = iconTypeID = attributes.Get('iconTypeID', 6)
        color = planetCommon.PLANET_COLOR_USED_PROCESSOR
        bgColor = (255 / 255.0,
         128 / 255.0,
         0 / 255.0,
         0.15)
        self.icon = uicontrols.Icon(parent=self, pos=(2, 2, 16, 16), state=uiconst.UI_DISABLED, typeID=iconTypeID, size=16, ignoreSize=True)
        gaugeCont = uiprimitives.Container(parent=self, pos=(0,
         0,
         self.width,
         self.width), align=uiconst.TOPLEFT)
        self.gauge = uiprimitives.Fill(parent=gaugeCont, align=uiconst.TOLEFT, width=0, color=color, state=uiconst.UI_DISABLED)
        uiprimitives.Fill(parent=gaugeCont, color=bgColor, state=uiconst.UI_DISABLED)
        self.subText = uicontrols.Label(text='', parent=self, top=22, state=uiconst.UI_DISABLED, fontsize=10)
        self.busy = False
        self.SetValue(self.value)

    def SetValue(self, value, frequency = 8.0):
        if self.busy or value == self.value:
            return
        if value > 1.0:
            value = 1.0
        uthread.new(self._SetValue, value, frequency)
        self.subText.text = '%i%%' % (value * 100)

    def _SetValue(self, value, frequency):
        if not self or self.destroyed:
            return
        self.busy = True
        self.value = value
        self.uiEffects.MorphUIMassSpringDamper(self.gauge, 'width', int(self.width * value), newthread=0, float=0, dampRatio=0.6, frequency=frequency, minVal=0, maxVal=self.width, maxTime=1.0)
        if not self or self.destroyed:
            return
        self.busy = False

    def GetMenu(self):
        ret = [(uiutil.MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, [self.typeID])]
        if session.role & ROLE_GML == ROLE_GML:
            ret.append(('GM / WM Extras', self.GetGMMenu()))
        return ret

    def GetGMMenu(self):
        return [('TypeID: %s' % self.typeID, blue.pyos.SetClipboardData, [str(int(self.typeID))]), ('Add commodity to pin', self.AddCommodity, [])]

    def AddCommodity(self):
        pinID = sm.GetService('planetUI').currentContainer.pin.id
        sm.GetService('planetUI').planet.GMAddCommodity(pinID, self.typeID)
