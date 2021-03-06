#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\eveEdit.py
from carbonui.control.basicDynamicScroll import Scroll
from carbonui.control.edit import EditCore
from carbonui.control.edit import FontAttribPanelCore
import _weakref
import evetypes
import uix
import util
import carbonui.const as uiconst
import uiutil
import log
import localization
import uiprimitives
from eve.client.script.ui.control.eveEdit_Parser import ParserBase

class Edit(EditCore):
    __guid__ = 'uicontrols.Edit'
    __notifyevents__ = ['OnUIScalingChange']
    default_align = uiconst.TOALL
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_fontcolor = (1.0, 1.0, 1.0, 0.75)

    def ApplyAttributes(self, attributes):
        EditCore.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)

    def OnUIScalingChange(self, *args):
        if not self.destroyed:
            self.DoContentResize()

    def OnDropDataDelegate(self, node, nodes):
        EditCore.OnDropDataDelegate(self, node, nodes)
        if self.readonly:
            return
        for entry in nodes:
            if entry.__guid__ in uiutil.AllUserEntries():
                link = 'showinfo:' + str(entry.info.typeID) + '//' + str(entry.charID)
                self.AddLink(entry.info.name, link)
            elif entry.__guid__ == 'listentry.PlaceEntry' and self.allowPrivateDrops:
                bookmarkID = entry.bm.bookmarkID
                bookmarkSvc = sm.GetService('bookmarkSvc')
                bms = bookmarkSvc.GetBookmarks()
                if bookmarkID in bms:
                    bookmark = bms[bookmarkID]
                    hint, comment = bookmarkSvc.UnzipMemo(bookmark.memo)
                link = 'showinfo:' + str(bms[bookmarkID].typeID) + '//' + str(bms[bookmarkID].itemID)
                self.AddLink(hint, link)
            elif entry.__guid__ == 'listentry.NoteItem' and self.allowPrivateDrops:
                link = 'note:' + str(entry.noteID)
                self.AddLink(entry.label, link)
            elif entry.__guid__ in ('listentry.InvItem', 'xtriui.InvItem', 'xtriui.ShipUIModule', 'listentry.InvAssetItem'):
                if type(entry.rec.itemID) is tuple:
                    link = 'showinfo:' + str(entry.rec.typeID)
                else:
                    link = 'showinfo:' + str(entry.rec.typeID) + '//' + str(entry.rec.itemID)
                self.AddLink(entry.name, link)
            elif entry.__guid__ == 'listentry.VirtualAgentMissionEntry':
                link = 'fleetmission:' + str(entry.agentID) + '//' + str(entry.charID)
                self.AddLink(entry.label, link)
            elif entry.__guid__ in ('listentry.CertEntry', 'listentry.CertEntryBasic'):
                link = 'CertEntry:%s//%s' % (entry.certID, entry.level)
                self.AddLink(entry.label, link)
            elif entry.__guid__ and entry.__guid__.startswith('listentry.ContractEntry'):
                link = 'contract:' + str(entry.solarSystemID) + '//' + str(entry.contractID)
                self.AddLink(entry.name.replace('&gt;', '>'), link)
            elif entry.__guid__ == 'listentry.FleetFinderEntry':
                link = 'fleet:%s' % entry.fleet.fleetID
                self.AddLink(entry.fleet.fleetName or localization.GetByLabel('UI/Common/Unknown'), link)
            elif entry.__guid__ in ('xtriui.ListSurroundingsBtn', 'listentry.LocationTextEntry', 'listentry.LabelLocationTextTop', 'listentry.LocationGroup', 'listentry.LocationSearchItem'):
                if not entry.typeID and not entry.itemID:
                    return
                link = 'showinfo:' + str(entry.typeID) + '//' + str(entry.itemID)
                displayLabel = getattr(entry, 'genericDisplayLabel', None) or entry.label
                self.AddLink(displayLabel, link)
            elif entry.__guid__ == 'listentry.FittingEntry':
                PADDING = 12
                link = 'fitting:' + sm.StartService('fittingSvc').GetStringForFitting(entry.fitting)
                roomLeft = self.RoomLeft() - PADDING
                if len(link) >= roomLeft:
                    if roomLeft < 14:
                        raise UserError('LinkTooLong')
                    if eve.Message('ConfirmTruncateLink', {'numchar': len(link),
                     'maxchar': roomLeft}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                        return
                    link = link[:roomLeft]
                self.AddLink(entry.fitting.name, link)
            elif entry.__guid__ in ('listentry.GenericMarketItem', 'uicls.GenericDraggableForTypeID', 'listentry.DroneEntry', 'listentry.SkillTreeEntry'):
                link = 'showinfo:' + str(entry.typeID)
                label = getattr(entry, 'label', None) or getattr(entry, 'text', '')
                self.AddLink(label, link)
            elif entry.__guid__ in ('listentry.KillMail', 'listentry.KillMailCondensed', 'listentry.WarKillEntry'):
                killmail = entry.mail
                hashValue = util.GetKillReportHashValue(killmail)
                if util.IsCharacter(killmail.victimCharacterID):
                    victimName = cfg.eveowners.Get(killmail.victimCharacterID).name
                    shipName = evetypes.GetName(killmail.victimShipTypeID)
                    label = localization.GetByLabel('UI/Corporations/Wars/Killmails/KillLinkCharacter', charName=victimName, typeName=shipName)
                else:
                    shipName = evetypes.GetName(killmail.victimShipTypeID)
                    label = localization.GetByLabel('UI/Corporations/Wars/Killmails/KillLinkStructure', typeName=shipName)
                link = 'killReport:%d:%s' % (entry.mail.killID, hashValue)
                self.AddLink(label, link)
            elif entry.__guid__ == 'listentry.WarEntry':
                warID = entry.war.warID
                attackerID = entry.war.declaredByID
                defenderID = entry.war.againstID
                attackerName = cfg.eveowners.Get(attackerID).name
                defenderName = cfg.eveowners.Get(defenderID).name
                label = localization.GetByLabel('UI/Corporations/Wars/WarReportLink', attackerName=attackerName, defenderName=defenderName)
                link = 'warReport:%d' % warID
                self.AddLink(label, link)
            elif entry.__guid__ == 'listentry.TutorialEntry':
                tutorialID = entry.tutorialID
                link = 'tutorial:%s' % tutorialID
                label = entry.label
                self.AddLink(label, link)
            elif entry.__guid__ == 'listentry.listentry.RecruitmentEntry':
                label = '%s - %s ' % (cfg.eveowners.Get(entry.advert.corporationID).name, entry.adTitle)
                link = 'recruitmentAd:' + str(entry.advert.corporationID) + '//' + str(entry.advert.adID)
                self.AddLink(label, link)
            elif entry.__guid__ == 'listentry.DirectionalScanResults':
                label = entry.typeName
                link = 'showinfo:' + str(entry.typeID) + '//' + str(entry.itemID)
                self.AddLink(label, link)
            elif entry.__guid__ in ('listentry.SkillEntry', 'listentry.SkillQueueSkillEntry'):
                label = entry.invtype.typeName
                link = 'showinfo:' + str(entry.invtype.typeID)
                self.AddLink(label, link)

    def ApplyGameSelection(self, what, data, changeObjs):
        if what == 6 and len(changeObjs):
            key = {}
            if data:
                key['link'] = data['link']
                t = self.DoSearch(key['link'], data['text'])
                if not t:
                    return
            else:
                format = [{'type': 'checkbox',
                  'label': '_hide',
                  'text': 'http://',
                  'key': 'http://',
                  'required': 1,
                  'setvalue': 1,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'btline'},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/Character'),
                  'key': 'char',
                  'required': 1,
                  'setvalue': 0,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/Corporation'),
                  'key': 'corp',
                  'required': 1,
                  'setvalue': 0,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'btline'},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/ItemType'),
                  'key': 'type',
                  'required': 1,
                  'setvalue': 0,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'btline'},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/SolarSystem'),
                  'key': 'solarsystem',
                  'required': 1,
                  'setvalue': 0,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/Station'),
                  'key': 'station',
                  'required': 1,
                  'setvalue': 0,
                  'frame': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'btline'},
                 {'type': 'edit',
                  'label': localization.GetByLabel('UI/Common/HtmlLink'),
                  'text': 'http://',
                  'labelwidth': 100,
                  'required': 1,
                  'key': 'txt',
                  'frame': 1}]
                key = self.AskLink(localization.GetByLabel('UI/Common/EnterLink'), format, width=400)
            anchor = -1
            if key:
                link = key['link']
                if link == None:
                    return
                if link in ('char', 'corp', 'solarsystem', 'station', 'type'):
                    if not self.typeID:
                        t = self.DoSearch(link, key['txt'])
                        if not t:
                            return
                    anchor = 'showinfo:' + str(self.typeID)
                    if self.itemID:
                        anchor += '//' + str(self.itemID)
                elif link == 'fleet':
                    anchor = 'fleet:' + str(self.itemID)
                elif link == 'http://':
                    if key['txt'].startswith(key['link']) or key['txt'].startswith('https://'):
                        anchor = ''
                    else:
                        anchor = key['link']
                    anchor += key['txt']
                else:
                    anchor = key['link'] + key['txt']
            return anchor
        return -1

    def OnLinkTypeChange(self, chkbox, *args):
        if chkbox.GetValue():
            self.itemID = self.typeID = 0
            self.key = chkbox.data['key']
            text = uiutil.GetChild(chkbox, 'text')
            wnd = chkbox.FindParentByName(localization.GetByLabel('UI/Common/GenerateLink'))
            if not wnd:
                return
            editParent = uiutil.FindChild(wnd, 'editField')
            if editParent is not None:
                label = uiutil.FindChild(editParent, 'label')
                label.text = text.text
                edit = uiutil.FindChild(editParent, 'edit_txt')
                edit.SetValue('')
                self.sr.searchbutt = uiutil.FindChild(editParent, 'button')
                if self.key in ('char', 'corp', 'type', 'solarsystem', 'station'):
                    if self.sr.searchbutt == None:
                        from eve.client.script.ui.control.buttons import Button
                        self.sr.searchbutt = Button(parent=editParent, label=localization.GetByLabel('UI/Common/SearchForItemType'), func=self.OnSearch, btn_default=0, align=uiconst.TOPRIGHT)
                    else:
                        self.sr.searchbutt.state = uiconst.UI_NORMAL
                    edit.width = 55
                elif self.sr.searchbutt != None:
                    self.sr.searchbutt.state = uiconst.UI_HIDDEN
                    edit.width = 0

    def OnSearch(self, *args):
        wnd = self.sr.searchbutt.FindParentByName(localization.GetByLabel('UI/Common/GenerateLink'))
        if not wnd:
            return
        editParent = uiutil.FindChild(wnd, 'editField')
        edit = uiutil.FindChild(editParent, 'edit_txt')
        val = edit.GetValue().strip().lower()
        name = self.DoSearch(self.key, val)
        if name is not None:
            edit.SetValue(name)

    def DoSearch(self, key, val):
        self.itemID = None
        self.typeID = None
        id = None
        name = ''
        if key == 'type':
            if getattr(self, 'markettypes', None) == None:
                from contractutils import GetMarketTypes
                self.markettypes = GetMarketTypes()
            itemTypes = []
            for t in self.markettypes:
                if t.typeName.lower().find(val.lower()) >= 0:
                    itemTypes.append((evetypes.GetName(t.typeID), None, t.typeID))

            if not itemTypes:
                eve.Message('NoItemTypesFound')
                return
            id = uix.ListWnd(itemTypes, 'item', localization.GetByLabel('UI/Common/SelectItemType'), None, 1)
        else:
            group = None
            hideNPC = 0
            if key == 'solarsystem':
                group = const.groupSolarSystem
            elif key == 'station':
                group = const.groupStation
            elif key == 'char':
                group = const.groupCharacter
            elif key == 'corp':
                group = const.groupCorporationOwner
            id = uix.Search(val, group, hideNPC=hideNPC, listType='Generic')
        name = ''
        if id:
            self.itemID = id
            self.typeID = 0
            if key in ('char', 'corp'):
                o = cfg.eveowners.Get(id)
                self.typeID = o.typeID
                name = o.name
            elif key == 'solarsystem':
                l = cfg.evelocations.Get(id)
                self.typeID = l.typeID
                name = l.name
            elif key == 'station':
                self.typeID = sm.GetService('ui').GetStation(id).stationTypeID
                l = cfg.evelocations.Get(id)
                name = l.name
            elif key == 'type':
                self.typeID = id[2]
                self.itemID = None
                name = id[0]
        return name

    def AskLink(self, label = '', lines = [], width = 280):
        icon = uiconst.QUESTION
        format = [{'type': 'btline'}, {'type': 'text',
          'text': label,
          'frame': 1}] + lines + [{'type': 'bbline'}]
        btns = uiconst.OKCANCEL
        retval = uix.HybridWnd(format, localization.GetByLabel('UI/Common/GenerateLink'), 1, None, uiconst.OKCANCEL, minW=width, minH=110, icon=icon)
        if retval:
            return retval
        else:
            return

    def AddLink(self, text, link = None):
        self.SetSelectionRange(None, None)
        text = uiutil.StripTags(text, stripOnly=['localized'])
        shiftCursor = len(text)
        node, obj, npos = self.GetNodeAndTextObjectFromGlobalCursor()
        if obj.letters:
            orgString = obj.letters
            orgIndex = node.stack.index(obj)
            obj.letters = orgString[:npos]
            firstSpaceObj = self.GetTextObject(' ')
            firstSpaceObj.a = None
            node.stack.insert(orgIndex + 1, firstSpaceObj)
            newObject = self.GetTextObject(' ')
            newObject.a = None
            node.stack.insert(orgIndex + 2, newObject)
            restObj = obj.Copy()
            restObj.letters = orgString[npos:]
            if restObj.letters:
                node.stack.insert(orgIndex + 3, restObj)
        else:
            newObject = obj
            newObject.a = None
        newObject.letters = text
        if link is not None:
            anchor = link
            attr = util.KeyVal()
            attr.href = anchor
            attr.alt = anchor
            newObject.a = attr
        endSpaceObj = newObject.Copy()
        endSpaceObj.letters = ' '
        endSpaceObj.a = None
        node.stack.insert(node.stack.index(newObject) + 1, endSpaceObj)
        self._OnResize(0)
        self.SetCursorPosAtObjectEnd(newObject)
        uicore.registry.SetFocus(self)


class FontAttribPanel(FontAttribPanelCore):
    __guid__ = 'uicls.FontAttribPanel'

    def Expand(self):
        self.expanding = 1
        if sm.GetService('connection').IsConnected():
            eve.Message('ComboExpand')
        log.LogInfo('Combo', self.name, 'expanding')
        colorpar = uiprimitives.Container(name='colors', align=uiconst.TOPLEFT, width=130, height=133)
        uicore.layer.menu.children.insert(0, colorpar)
        colorscroll = Scroll(parent=colorpar)
        colors = [((1.0, 1.0, 1.0, 1.0), 'white'),
         ((0.7, 0.7, 0.7, 1.0), 'grey 70%'),
         ((0.3, 0.3, 0.3, 1.0), 'grey 30%'),
         ((0.0, 0.0, 0.0, 1.0), 'black'),
         ((1.0, 1.0, 0.0, 1.0), 'yellow'),
         ((0.0, 1.0, 0.0, 1.0), 'green'),
         ((1.0, 0.0, 0.0, 1.0), 'red'),
         ((0.0, 0.0, 1.0, 1.0), 'blue'),
         ((0.5, 0.5, 0.0, 1.0), 'dark yellow'),
         ((0.0, 0.5, 0.0, 1.0), 'dark green'),
         ((0.5, 0.0, 0.0, 1.0), 'dark red'),
         ((0.0, 0.0, 0.5, 1.0), 'dark blue'),
         ((0.5, 0.0, 0.5, 1.0), 'dark mangenta'),
         ((0.0, 1.0, 1.0, 1.0), 'cyan'),
         ((1.0, 0.0, 1.0, 1.0), 'mangenta'),
         ((0.0, 0.5, 1.0, 1.0), 'dark blue'),
         ((1.0, 0.5, 0.0, 1.0), 'dark blue')]
        x = y = 0
        scrolllist = []
        icons = []
        import listentry
        for each in colors:
            color, labelstr = each
            icons.append((None,
             color,
             color,
             self.PickCol))
            x += 1
            if x == 4:
                scrolllist.append(listentry.Get('Icons', {'icons': icons}))
                icons = []
                y += 1
                x = 0

        colorscroll.Load(32, contentList=scrolllist)
        colorpar.left, colorpar.top = self.sr.color.absoluteLeft, [self.sr.color.absoluteTop + self.sr.color.height, self.sr.color.absoluteTop - colorpar.height][self.sr.color.absoluteTop + self.sr.color.height + colorpar.height > uicore.desktop.height]
        colorpar.state = uiconst.UI_NORMAL
        self.sr.colorpar = _weakref.ref(colorscroll)
        uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalClick)
        self.expanding = 0
        self.expanded = 1
        log.LogInfo('Colors', self.name, 'expanded')


from carbonui.control.edit import EditCoreOverride, FontAttribPanelCoreOverride
EditCoreOverride.__bases__ = (Edit,)
FontAttribPanelCoreOverride.__bases__ = (FontAttribPanel,)
