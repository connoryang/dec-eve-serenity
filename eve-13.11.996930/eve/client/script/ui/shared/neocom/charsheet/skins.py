#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\skins.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from collections import defaultdict
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.skins.skinSvc import Skin
from eve.client.script.ui.shared.skins.skinPanel import SkinDurationLabel
from functools import partial
import evetypes
from itertoolsext import bucket, count
import localization
SETTING_SHOW_SKINS = 'charsheet_skins_showSkins'
SHOW_ALL_SKINS = 'all_skins'
SHOW_ACTIVE_SKINS = 'active_skins'
SHOW_INACTIVE_SKINS = 'inactive_skins'
SETTING_DEFAULTS = {SETTING_SHOW_SKINS: SHOW_ALL_SKINS}

class CharacterSkinsPanel(Container):

    def ApplyAttributes(self, attributes):
        super(CharacterSkinsPanel, self).ApplyAttributes(attributes)
        self.Layout()

    def Layout(self):
        menuBar = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padBottom=4)
        UtilMenu(parent=menuBar, align=uiconst.CENTERLEFT, menuAlign=uiconst.BOTTOMLEFT, GetUtilMenu=self.GetSettingsMenu, texturePath='res:/UI/Texture/SettingsCogwheel.png', width=16, height=16, iconSize=18)
        self.filter = QuickFilterEdit(parent=menuBar, align=uiconst.CENTERLEFT, left=18, width=150)
        self.filter.ReloadFunction = self.Load
        self.scroll = Scroll(parent=self, align=uiconst.TOALL)

    @property
    def filterText(self):
        return self.filter.GetValue().strip().lower()

    def Load(self):
        self.scroll.Clear()
        skinsByMaterialID = self._GetFilteredSkinsByMaterialID()
        entries = []
        for materialID, skins in skinsByMaterialID.iteritems():
            entry = self._CreateMaterialGroupEntry(materialID, skins)
            if entry is not None:
                entries.append(entry)

        self.scroll.Load(contentList=sorted(entries, key=lambda e: e.label), noContentHint=localization.GetByLabel('UI/SkillQueue/NoResultsForFilters'))

    def _GetFilteredSkinsByMaterialID(self):
        skinSvc = sm.GetService('skinSvc')
        licensedSkinsByID = {s.skinID:s for s in skinSvc.GetLicensedSkins()}
        skins = []
        for staticSkin in skinSvc.static.GetAllSkins():
            licensedSkin = licensedSkinsByID.get(staticSkin.skinID, None)
            skins.append(self._CreateSkinObject(staticSkin, licensedSkin))

        show = GetSetting(SETTING_SHOW_SKINS)
        if show == SHOW_ACTIVE_SKINS:
            skins = filter(lambda s: s.licensed, skins)
        elif show == SHOW_INACTIVE_SKINS:
            skins = filter(lambda s: not s.licensed, skins)
        return bucket(skins, keyprojection=lambda s: s.materialID)

    def _CreateSkinObject(self, staticSkin, licensedSkin = None):
        material = sm.GetService('skinSvc').static.GetMaterialByID(staticSkin.skinMaterialID)
        licensed = licensedSkin is not None
        expires = licensedSkin.expires if licensedSkin else None
        return Skin(material, skin=staticSkin, licensed=licensed, expires=expires)

    def _CreateMaterialGroupEntry(self, materialID, skins):
        skinsByShipID = self._GroupAndFilterByShip(skins)
        if not skinsByShipID:
            return None
        material = sm.GetService('skinSvc').GetStaticMaterialByID(materialID)
        owned = count((ship for ship, skins in skinsByShipID.iteritems() if any((s.licensed for s in skins))))
        label = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkinsGroupWithCount', groupName=material.name, skinsOwned=owned, skinsTotal=len(skinsByShipID))
        data = {'label': label,
         'id': ('SkinMaterials', material.materialID),
         'showicon': material.iconTexturePath,
         'groupItems': skinsByShipID,
         'GetSubContent': self._GetSkinsSubContent,
         'showlen': False,
         'BlockOpenWindow': True,
         'state': 'locked'}
        return listentry.Get('Group', data=data)

    def _GroupAndFilterByShip(self, skins):
        skinsByShipID = defaultdict(list)
        for skin in skins:
            for shipTypeID in skin.types:
                if self._IsFilterMatch(shipTypeID, skin):
                    skinsByShipID[shipTypeID].append(skin)

        return skinsByShipID

    def _IsFilterMatch(self, shipTypeID, skin):
        if len(self.filterText) == 0:
            return True
        shipName = evetypes.GetName(shipTypeID).lower()
        skinName = skin.name.lower()
        return self.filterText in shipName or self.filterText in skinName

    def _GetSkinsSubContent(self, nodedata, *args):
        skinsByShipID = nodedata.groupItems
        nodes = []
        for shipTypeID, skins in skinsByShipID.iteritems():
            skin = self._PickRepresentingSkin(skins)
            data = {'typeID': shipTypeID,
             'itemID': None,
             'label': evetypes.GetName(shipTypeID),
             'getIcon': True,
             'sublevel': 1,
             'skin': skin}
            entry = listentry.Get(decoClass=ShipSkinEntry, data=data)
            nodes.append(entry)

        nodes = sorted(nodes, key=lambda x: x.label)
        return nodes

    def _PickRepresentingSkin(self, skins):
        licensedSkins = filter(lambda s: s.licensed, skins)
        if not licensedSkins:
            return skins[0]
        else:
            permanentSkins = filter(lambda s: s.expires is None, licensedSkins)
            if permanentSkins:
                return permanentSkins[0]
            limitedSkins = filter(lambda s: s.expires, licensedSkins)
            limitedSkins = sorted(limitedSkins, key=lambda s: s.expires, reverse=True)
            return limitedSkins[0]

    def GetSettingsMenu(self, menuParent):
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Skins/ShowAllSkins'), checked=GetSetting(SETTING_SHOW_SKINS) == SHOW_ALL_SKINS, callback=partial(self.SetSettingAndReload, SETTING_SHOW_SKINS, SHOW_ALL_SKINS))
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Skins/ShowActiveSkins'), checked=GetSetting(SETTING_SHOW_SKINS) == SHOW_ACTIVE_SKINS, callback=partial(self.SetSettingAndReload, SETTING_SHOW_SKINS, SHOW_ACTIVE_SKINS))
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Skins/ShowInactiveSkins'), checked=GetSetting(SETTING_SHOW_SKINS) == SHOW_INACTIVE_SKINS, callback=partial(self.SetSettingAndReload, SETTING_SHOW_SKINS, SHOW_INACTIVE_SKINS))

    def SetSettingAndReload(self, key, value):
        SetSetting(key, value)
        self.Load()


class ShipSkinEntry(listentry.Item):

    def Startup(self, *args):
        super(ShipSkinEntry, self).Startup(*args)

    def Load(self, node):
        super(ShipSkinEntry, self).Load(node)
        if node.skin.licensed:
            self.sr.label.opacity = 1
        else:
            self.sr.label.opacity = 0.5
            self.sr.icon.opacity = 0.5
        if node.skin.licensed:
            grid = LayoutGrid(parent=self, align=uiconst.CENTERRIGHT, columns=2, left=20)
            EveLabelMedium(parent=grid, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Skins/Active'))
            SkinDurationLabel(parent=grid, skin=node.skin)


def GetSetting(key):
    return settings.user.ui.Get(key, SETTING_DEFAULTS[key])


def SetSetting(key, value):
    settings.user.ui.Set(key, value)
