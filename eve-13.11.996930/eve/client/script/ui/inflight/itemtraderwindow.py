#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\itemtraderwindow.py
from eve.client.script.ui.control.eveWindow import Window
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.line import Line
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.buttons import Button
from localization import GetByLabel
from eve.client.script.ui.control.eveIcon import Icon
import evetypes
import blue

class ItemTraderWindow(Window):
    __guid__ = 'form.ItemTraderWindow'
    default_topParentHeight = 0
    default_minSize = (300, 425)
    default_windowID = 'itemTrader'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.itemTrader = attributes.itemTrader
        self.shipId = attributes.shipId
        self.cargoChecker = attributes.cargoChecker
        self.default_caption = evetypes.GetName(self.itemTrader.typeID)
        self.ConstructButtons()
        self.mainContainer = Container(name='mainContainer', parent=self.sr.main)
        self.ConstructInputSection()
        self.outputSection = None

    def ConstructButtons(self):
        buttonParent = FlowContainer(name='buttonParent', parent=self.sr.main, align=uiconst.TOBOTTOM, padding=6, autoHeight=True, centerContent=True, contentSpacing=(6, 6))
        self.acceptButton = Button(parent=buttonParent, label=GetByLabel('UI/PVPTrade/Accept'), func=self.Accept, align=uiconst.NOALIGN)
        Button(parent=buttonParent, label=GetByLabel('UI/Common/Buttons/Cancel'), func=self.Close, align=uiconst.NOALIGN)
        self.CanPlayerAcceptTrade()

    def ConstructInputSection(self):
        self.inputSection = Container(name='inputSection', parent=self.mainContainer, align=uiconst.TOTOP_PROP, height=0.5, padding=(5, 0, 5, 0))
        self.inputHeader = Container(name='inputHeader', parent=self.inputSection, align=uiconst.TOTOP, height=50)
        Label(parent=self.inputHeader, text=GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/RequiredItems', itemCount=2), fontsize=25, align=uiconst.CENTER)
        Line(parent=self.inputHeader, align=uiconst.TOBOTTOM)
        self.inputListSection = ScrollContainer(name='inputListSection', parent=self.inputSection, align=uiconst.TOTOP, height=128)
        self.PopulateItemsToScroll(self.inputListSection, self.itemTrader.GetInputItems())

    def Accept(self, *args):
        if not self.CanPlayerAcceptTrade():
            return
        success = self.ProcessTrade()
        if success:
            self.ConstructOutputSection()
        self.CanPlayerAcceptTrade()

    def PopulateItemsToScroll(self, scroll, items):
        for typeId, quantity in items.iteritems():
            itemContainer = Container(parent=scroll, align=uiconst.TOTOP, height=64)
            Line(parent=itemContainer, align=uiconst.TOBOTTOM)
            Icon(parent=itemContainer, typeID=typeId, align=uiconst.CENTERLEFT)
            labelContainer = Container(parent=itemContainer, align=uiconst.TOALL, padding=(64, 0, 64, 0))
            Label(parent=labelContainer, text=evetypes.GetName(typeId), fontsize=10, align=uiconst.CENTER, width=128)
            quantityContainer = Container(parent=itemContainer, align=uiconst.TORIGHT, width=64)
            Label(parent=quantityContainer, text=GetByLabel('UI/Common/Quantity') + ' ' + str(quantity), fontsize=10, align=uiconst.CENTER)

    def ConstructOutputSection(self):
        self.CloseOutputSection()
        blue.pyos.synchro.Sleep(1000)
        self.CloseOutputSection()
        self.outputSection = Container(name='outputSection', parent=self.mainContainer, align=uiconst.TOTOP_PROP, height=0.5, padding=(5, 0, 5, 0))
        self.outputHeader = Container(name='outputHeader', parent=self.outputSection, align=uiconst.TOTOP, height=50)
        Label(parent=self.outputHeader, text=GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/DeliveredItems', itemCount=2), fontsize=25, align=uiconst.CENTER)
        Line(parent=self.outputHeader, align=uiconst.TOBOTTOM)
        self.outputListSection = ScrollContainer(name='outputListSection', parent=self.outputSection, align=uiconst.TOTOP, height=128)
        self.PopulateItemsToScroll(self.outputListSection, self.itemTrader.GetOutputItems())

    def CanPlayerAcceptTrade(self):
        if not self.cargoChecker.IsRequiredCargoSpaceAvailable():
            self.acceptButton.Disable()
            self.acceptButton.hint = GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/LackOfCargo')
            return False
        if not self.cargoChecker.AreRequiredItemsPresent():
            self.acceptButton.Disable()
            self.acceptButton.hint = GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/MissingItem')
            return False
        self.acceptButton.Enable()
        self.acceptButton.hint = ''
        return True

    def ProcessTrade(self):
        return self.itemTrader.ProcessTrade()

    def CloseOutputSection(self):
        if self.outputSection:
            self.outputSection.Close()
