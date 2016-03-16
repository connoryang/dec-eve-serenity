#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\svc_dgmattr.py
import sys
import itertools
import uiutil
import util
from service import ROLE_GMH, ROLE_PROGRAMMER
from htmlwriter import HTMLEncode
import eve.common.lib.appConst as const
import eve.client.script.ui.control.entries as listentry
from eve.common.script.net.eveMoniker import GetLocationBindParams
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from carbonui.primitives.container import Container
from dogma.dogmaLogging import LogNotice
from dogma.dogmaLogging import EvalArgs as EA
import log
import re

class AttributeDetailsWindow(Window):
    default_caption = 'My Window Caption'
    default_windowID = 'attributeDetailsWindow'
    default_topParentHeight = 0

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.default_caption = attributes.Get('caption', self.default_caption)
        bodyText = attributes.bodyText
        parent = self.sr.main
        EditPlainText(name='myTextEdit', parent=parent, align=uiconst.TOALL, setvalue=bodyText)
        textWidth, textHeight = Label.MeasureTextSize(bodyText)
        self.width, self.height = textWidth + 20, textHeight + 40


class AttrEntry(listentry.Generic):
    __guid__ = 'listentry.DgmAttrEntry'

    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)
        self.colorcodedFill = Fill(bgParent=self, color=(0, 0, 0, 0))

    def Load(self, node):
        listentry.Generic.Load(self, node)
        self.colorcodedFill.SetRGB(*node.color)

    def OnDblClick(self, *args):
        self.ShowAttributeDetailsFromServer()

    def GetMenu(self):
        n = self.sr.node
        ret = [('View Details (+ Server Graph)', self.ShowAttributeDetailsFromServer, ()), ('View Details (+ Client Graph)', self.ShowAttributeDetailsFromClient, ())]
        if eve.session.role & ROLE_PROGRAMMER:
            if n.attributeName == 'charge':
                return ret
            ret.append(('Change Attribute', sm.StartService('menu').SetDogmaAttribute, (n.itemID, n.attributeName, n.actualValue)))
        return ret

    def ShowAttributeDetailsFromServer(self):
        n = self.sr.node
        n.ShowAttribute(n.attributeID, showServerSideGraph=True)

    def ShowAttributeDetailsFromClient(self):
        n = self.sr.node
        n.ShowAttribute(n.attributeID, showServerSideGraph=False)


class AttributeInspector(Window):
    __guid__ = 'form.AttributeInspector'
    default_windowID = 'AttributeInspector'

    def __init__(self, **kwargs):
        super(AttributeInspector, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.itemID = attributes.itemID
        self.typeID = attributes.typeID
        self.nameFilter = None
        self.stateManager = sm.GetService('godma').GetStateManager()
        self.SetCaption('Attribute Inspector')
        self.SetWndIcon(None)
        self.SetTopparentHeight(0)
        main = Container(name='main', parent=uiutil.GetChild(self, 'main'), pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        top = Container(name='top', parent=main, height=20, align=uiconst.TOTOP)
        Button(parent=top, label='Refresh', align=uiconst.TORIGHT, func=self.Refresh)
        self.input = SinglelineEdit(name='itemID', parent=top, width=-1, height=-1, align=uiconst.TOALL)
        self.input.readonly = not eve.session.role & ROLE_GMH
        self.input.OnReturn = self.Refresh
        self.input.SetValue(str(self.itemID))
        Container(name='div', parent=main, height=5, align=uiconst.TOTOP)
        self.scroll = Scroll(parent=main)
        self.Refresh()

    def _GetListEntryForAttr(self, attrID, attrName, clientValsByAttrID, godmaValsByAttrID, serverValsByAttrID, baseValsByAttrID):
        notApplicable = '<color=green>[n/a]</color>'
        try:
            clientValue = clientValsByAttrID[attrID]
        except KeyError:
            clientValue = notApplicable

        try:
            godmaValue = self.stateManager.GetAttribute(self.itemID, attrName)
        except KeyError:
            godmaValue = notApplicable

        try:
            serverValue = serverValsByAttrID[attrID]
        except KeyError:
            serverValue = notApplicable

        try:
            baseValue = baseValsByAttrID[attrID]
        except KeyError:
            baseValue = notApplicable

        color = (0, 0, 0, 0)
        if godmaValue != serverValue:
            color = (1, 0, 0, 0.25)
        elif baseValue == notApplicable:
            color = (1, 1, 0, 0.25)
        baseColor = serverColor = clientColor = godmaColor = ''
        if clientValue != godmaValue:
            if clientValue == serverValue:
                clientColor = 'yellow'
            elif clientValue == baseValue:
                clientColor = 'blue'
            else:
                clientColor = 'red'
        if godmaValue != serverValue:
            if godmaValue == baseValue:
                godmaColor = 'blue'
            else:
                godmaColor = 'red'
        if serverValue != baseValue:
            serverColor = 'yellow'
        colorize = '<color={}>{}</color>'
        if clientColor:
            clientValue = colorize.format(clientColor, clientValue)
        if godmaColor:
            godmaValue = colorize.format(godmaColor, godmaValue)
        if serverColor:
            serverValue = colorize.format(serverColor, serverValue)
        entry = listentry.Get('DgmAttrEntry', {'label': u'{attrID}<t>{attrName}<t>{clientValue}<t>{godmaValue}<t>{serverValue}<t>{baseValue}'.format(**locals()),
         'color': color,
         'attributeID': attrID,
         'attributeName': attrName,
         'actualValue': godmaValue,
         'baseValue': baseValue,
         'ShowAttribute': self.ShowAttribute,
         'itemID': self.itemID})
        return entry

    def AttrID_FromName(self, attrName):
        attrID = self.stateManager.attributesByName[attrName].attributeID
        return attrID

    def AttrName_FromID(self, attrID):
        attrName = self.stateManager.attributesByID[attrID].attributeName
        return attrName

    def _GetClientValsByAttrID(self):
        cDLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
        try:
            clientDogmaAttribs = cDLM.dogmaItems[self.itemID].attributes
            clientValsByAttribID = {attrID:clientDogmaAttribs[attrID].GetValue() for attrID in clientDogmaAttribs}
        except KeyError:
            clientValsByAttribID = {}

        return clientValsByAttribID

    def _GetGodmaValsByAttrID(self):
        godmaValsByAttributeName = self.stateManager.GetAttributes(self.itemID)
        godmaValsByAttributeID = {self.AttrID_FromName(name):val for name, val in godmaValsByAttributeName.iteritems()}
        return godmaValsByAttributeID

    def _GetServerValsByAttrID(self):
        serverValsByAttribID = self.GetServerDogmaLM().QueryAllAttributesForItem(self.itemID)
        return serverValsByAttribID

    def _GetBaseValsByAttrID(self):
        baseValsByAttribID = sm.GetService('info').GetAttributeDictForType(self.typeID)
        return baseValsByAttribID

    def Refresh(self, *args):
        inputValue = self.input.GetValue()
        subLocPattern = '\\(\\d*L?, \\d*, \\d*\\)'
        subLocPart = re.match(subLocPattern, inputValue)
        if subLocPart:
            itemKey = subLocPart.group(0)
            itemID, flagID, typeID = itemKey.replace('(', '').replace(')', '').split(',')
            self.itemID = (long(itemID), int(flagID), int(typeID))
            self.typeID = int(typeID)
        else:
            itemID = int(filter('0123456789'.__contains__, inputValue))
            if itemID != self.itemID or not self.typeID:
                self.itemID = itemID
                self.typeID = None
                m = util.Moniker('i2', GetLocationBindParams())
                if m.IsPrimed(self.itemID):
                    self.typeID = m.GetItem(self.itemID).typeID
        nameFilter = inputValue.replace(str(self.itemID), '').lstrip().rstrip()
        if nameFilter != self.nameFilter and (nameFilter.isalpha() or nameFilter == ''):
            self.nameFilter = nameFilter
        log.LogInfo('Refresh: itemID = %s, typeID = %s, nameFilter = %s' % (self.itemID, self.typeID, self.nameFilter or 'None'))
        contentList = []
        if self.typeID:
            clientValsByAttrID = self._GetClientValsByAttrID()
            godmaValsByAttrID = self._GetGodmaValsByAttrID()
            serverValsByAttrID = self._GetServerValsByAttrID()
            baseValsByAttrID = self._GetBaseValsByAttrID()
            allMyAttribIDs = set(itertools.chain(clientValsByAttrID, godmaValsByAttrID, serverValsByAttrID, baseValsByAttrID))
            for attrID in allMyAttribIDs:
                attrName = self.AttrName_FromID(attrID)
                if not self.nameFilter or self.nameFilter.lower() in attrName.lower():
                    contentList.append(self._GetListEntryForAttr(attrID, attrName, clientValsByAttrID, godmaValsByAttrID, serverValsByAttrID, baseValsByAttrID))

        self.scroll.Load(contentList=contentList, headers=['ID',
         'Name',
         'ClientVal',
         'GodmaVal',
         'ServerVal',
         'Base'], fixedEntryHeight=18)
        self.scroll.Sort('Name')

    def GetServerDogmaLM(self):
        return self.stateManager.GetDogmaLM()

    def ShowAttribute(self, attributeID, showServerSideGraph = True):
        l = locals
        attrName = self.stateManager.attributesByID[attributeID].attributeName
        try:
            godmaVal = self.stateManager.GetAttribute(self.itemID, attrName)
        except (KeyError, RuntimeError, ZeroDivisionError):
            sys.exc_clear()
            godmaVal = '[None]'

        serverValue, baseValue, extraInfo = self.GetDetailedServerValues(self.itemID, attributeID, godmaVal)
        if not showServerSideGraph:
            clientDogmaIM = sm.GetService('clientDogmaIM')
            clientDogmaLM = clientDogmaIM.GetDogmaLocation()
            extraInfo = ['Client-side Graph:', '']
            clientGraph = clientDogmaLM.DescribeModifierGraphForDebugWindow(self.itemID, attributeID).split('\n')
            extraInfo += clientGraph
        x = ['Godma/Server/Base values: {} {} {}'.format(godmaVal, serverValue, baseValue), ''] + extraInfo
        x = [ HTMLEncode(s) for s in x ]
        title = 'Attribute Info: %s' % attrName
        bodyText = '<br>'.join(x)
        newWindow = AttributeDetailsWindow(caption=title, bodyText=bodyText)
        newWindow.SetActive()

    def GetDetailedServerValues(self, itemID, attributeID, godmaVal):
        l = locals
        sDLM = self.GetServerDogmaLM()
        descr = sDLM.FullyDescribeAttribute(itemID, attributeID, 'Just Inspecting -- Godma Value on client was %s.' % godmaVal)
        serverValue = descr[2].split(':')[1]
        baseValue = descr[3].split(':')[1]
        extraInfo = descr[4:]
        extraInfo[0] = extraInfo[0].replace('Attribute modification graph:', 'Server-side graph:')
        queriedValue = sDLM.QueryAttributeValue(itemID, attributeID)
        if str(queriedValue) != serverValue:
            LogNotice('INCONSISTENT!')
        return (serverValue, baseValue, extraInfo)
