#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\baseFitting.py
from eve.client.script.ui.shared.fitting.fittingCenter import FittingCenter
from eve.client.script.ui.shared.fitting.fittingUtil import GetBaseShapeSize, GetTypeAttributesByID, FITKEYS
from eve.client.script.ui.shared.fitting.slotAdder import HardpointAdder
import evetypes
from shipfitting.fittingStuff import GetSlotTypeForType
from localization import GetByLabel, GetByMessageID
from carbonui.primitives.container import Container
import carbonui.const as uiconst
import dogma.const as dogmaConst

class Fitting(Container):
    __notifyevents__ = ['OnStartSlotLinkingMode', 'OnResetSlotLinkingMode']
    __guid__ = 'baseFitting'
    default_width = 640
    default_height = 640
    default_align = uiconst.CENTERLEFT
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.controller = attributes.controller
        self.controller.on_new_itemID.connect(self.UpdateStats)
        self.controller.on_stats_changed.connect(self.UpdateStats)
        self.controller.on_item_ghost_fitted.connect(self.HiliteMatchingSlot)
        self.isDelayedAnim = False
        self.menuSlots = {}
        self.lastAddition = (0.0, 0.0, 0.0)
        self.updateStatsThread = None
        self.updateStatsArgs = (None, None)
        self.slots = {}
        self.controller.WaitForShip()
        self.SetSizeVariables()
        self.fittingCenter = FittingCenter(parent=self, idx=0, controller=self.controller)
        self.slots = self.fittingCenter.GetSlots()
        self.AddTurretAndLauncherMarkers()
        self.UpdateStats()
        uicore.animations.FadeTo(self, 0.0, 1.0, duration=1.0)

    def SetSizeVariables(self):
        baseShapeSize = GetBaseShapeSize()
        self.width = baseShapeSize
        self.height = baseShapeSize

    def AddTurretAndLauncherMarkers(self):
        cX = cY = GetBaseShapeSize() / 2
        turretAdder = HardpointAdder(const.attributeTurretSlotsLeft, cX, cY, isleftSide=True)
        turretAdder.AddIcon(self, 'ui_26_64_1', self.LoadTooltipPanelForTurret)
        turretAdder.AddMarkers(self)
        self.turretSlots = turretAdder.slots
        launcherAdder = HardpointAdder(const.attributeLauncherSlotsLeft, cX, cY)
        launcherAdder.AddIcon(self, 'ui_81_64_16', self.LoadTooltipPanelForLauncher)
        launcherAdder.AddMarkers(self)
        self.launcherSlots = launcherAdder.slots

    def LoadTooltipPanelForTurret(self, tooltipPanel, *args):
        turretsFitted = self.controller.GetNumTurretsFitted()
        turretSlotsLeft = self.controller.GetNumTurretHardpointsLeft()
        counterText = GetByLabel('Tooltips/FittingWindow/TurretHardPointBubbles_description', hardpointsUsed=int(turretsFitted), hardpointsTotal=int(turretsFitted + turretSlotsLeft))
        return self.LoadTooltipPanelForTurretsAndLaunchers(tooltipPanel, const.attributeTurretSlotsLeft, counterText)

    def LoadTooltipPanelForLauncher(self, tooltipPanel, *args):
        turretsFitted = self.controller.GetNumLaunchersFitted()
        turretSlotsLeft = self.controller.GetNumLauncherHardpointsLeft()
        counterText = GetByLabel('Tooltips/FittingWindow/LauncherHardPointBubbles_description', hardpointsUsed=int(turretsFitted), hardpointsTotal=int(turretsFitted + turretSlotsLeft))
        return self.LoadTooltipPanelForTurretsAndLaunchers(tooltipPanel, const.attributeLauncherSlotsLeft, counterText)

    def LoadTooltipPanelForTurretsAndLaunchers(self, tooltipPanel, attributeID, counterText):
        attribute = cfg.dgmattribs.Get(attributeID)
        headerText = GetByMessageID(attribute.tooltipTitleID)
        descriptionText = GetByMessageID(attribute.tooltipDescriptionID)
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=headerText, bold=True)
        tooltipPanel.AddLabelMedium(text=counterText, bold=True, align=uiconst.TOPRIGHT, cellPadding=(20, 0, 0, 0))
        tooltipPanel.AddLabelMedium(text=descriptionText, wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))

    def ShowAddition(self, h, m, l):
        if (h, m, l) == self.lastAddition:
            return
        self.lastAddition = (h, m, l)
        numHi = self.controller.GetNumHiSlots()
        numMed = self.controller.GetNumMedSlots()
        numLow = self.controller.GetNumLowSlots()
        for i, totalslots in enumerate((numHi, numMed, numLow)):
            add = [h, m, l][i]
            modslots = add + totalslots
            for sidx in xrange(8):
                flag = getattr(const, 'flag%sSlot%s' % (FITKEYS[i], sidx))
                slot = self.slots[flag]
                if sidx < modslots:
                    if sidx >= totalslots:
                        slot.ColorUnderlay((1.0, 1.0, 0.0))
                        slot.Hilite(1)
                        slot.opacity = 1.0
                    else:
                        slot.ColorUnderlay()
                        if slot.state == uiconst.UI_DISABLED:
                            slot.opacity = 0.25
                        else:
                            slot.opacity = 1.0
                elif sidx >= totalslots:
                    slot.ColorUnderlay()
                    if slot.state == uiconst.UI_DISABLED:
                        slot.opacity = 0.25
                    else:
                        slot.opacity = 1.0
                else:
                    slot.ColorUnderlay((1.0, 0.0, 0.0))
                    slot.Hilite(1)
                    slot.opacity = 1.0

    def OnStartSlotLinkingMode(self, typeID, *args):
        for flag, icon in self.slots.iteritems():
            if getattr(icon, 'module', None):
                if icon.module.typeID != typeID:
                    if hasattr(icon, 'color'):
                        icon.linkDragging = 1
                        icon.color.a = 0.1

    def OnResetSlotLinkingMode(self, *args):
        for flag, icon in self.slots.iteritems():
            if getattr(icon, 'module', None):
                if getattr(icon, 'linkDragging', None):
                    icon.linkDragging = 0
                    if hasattr(icon, 'color'):
                        icon.color.a = 1.0

    def HiliteMatchingSlot(self):
        hiliteSlotFlag = None
        powerType = None
        ghostTypeID = self.controller.GetGhostFittedTypeID()
        if ghostTypeID:
            if ghostTypeID in cfg.dgmtypeattribs:
                for attribute in cfg.dgmtypeattribs[ghostTypeID]:
                    if attribute.attributeID == const.attributeSubSystemSlot:
                        hiliteSlotFlag = int(attribute.value)
                        break

            if hiliteSlotFlag is None:
                if ghostTypeID in cfg.dgmtypeeffects:
                    powerType = GetSlotTypeForType(ghostTypeID)
        for slot in self.slots.itervalues():
            slot.HiliteIfMatching(hiliteSlotFlag, powerType)

    def AddToSlotsWithMenu(self, slot):
        self.menuSlots[slot] = 1

    def ClearSlotsWithMenu(self):
        for slot in self.menuSlots.iterkeys():
            slot.HideUtilButtons()

        self.menuSlots = {}

    def UpdateStats(self):
        self.UpdateShipHardpoints()
        self.UpdateSlotAddition()

    def UpdateSlotAddition(self):
        typeID = self.controller.GetGhostFittedTypeID()
        typeAttributesByID = GetTypeAttributesByID(typeID)
        lowSlotAddition, medSlotAddition, hiSlotAddition = self.controller.GetSlotAdditionInfo(typeAttributesByID)
        hiSlotAddition += typeAttributesByID.get(dogmaConst.attributeHiSlotModifier, 0.0)
        medSlotAddition += typeAttributesByID.get(dogmaConst.attributeMedSlotModifier, 0.0)
        lowSlotAddition += typeAttributesByID.get(dogmaConst.attributeLowSlotModifier, 0.0)
        self.ShowAddition(hiSlotAddition, medSlotAddition, lowSlotAddition)

    def UpdateShipHardpoints(self):
        typeID = self.controller.GetGhostFittedTypeID()
        launchersFitted, turretsFitted = self.controller.GetNumTurretsAndLaunchersFitted()
        typeAttributesByID = GetTypeAttributesByID(typeID)
        turretAddition, launcherAddition = self.controller.GetHardpointAdditionInfo(typeAttributesByID)
        turretSlotsLeft = self.controller.GetNumTurretHardpointsLeft()
        launcherSlotsLeft = self.controller.GetNumLauncherHardpointsLeft()
        hardpointSlotInfo = [(self.turretSlots,
          turretSlotsLeft,
          turretsFitted,
          turretAddition,
          self.LoadTooltipPanelForTurret), (self.launcherSlots,
          launcherSlotsLeft,
          launchersFitted,
          launcherAddition,
          self.LoadTooltipPanelForLauncher)]
        for slotSet, slotsLeft, slotsFitted, slotsAddition, tooltipLoadFunc in hardpointSlotInfo:
            for i, slot in enumerate(slotSet):
                slot.ModifyLook(i, slotsLeft, slotsFitted, slotsAddition)
                slot.LoadTooltipPanel = tooltipLoadFunc
