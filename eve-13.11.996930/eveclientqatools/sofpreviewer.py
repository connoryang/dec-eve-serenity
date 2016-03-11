#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveclientqatools\sofpreviewer.py
import blue
import uicontrols
import carbonui.const as uiconst
import evegraphics.utils as gfxutils
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.shared.preview import PreviewContainer
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from carbonui.control.slider import Slider
from sofDnaLibrary.query import GetDnaStringMatchingQuery
DEFAULT_FACTION_FOR_T2HULLS = {'ardishapur': ['ac2_t2b',
                'ai2_t2',
                'af5_t2',
                'ab2_t2',
                'af2_t2',
                'ac4_t2'],
 'brutor': ['mf1_t2a',
            'mcb1_t2c',
            'mf5_t2a',
            'mc3_t2a',
            'mf7_t2c',
            'mc2_t2a',
            'mbc2_t2',
            'mb2_t2',
            'mf4_t2a',
            'mdh1_t2',
            'mdl1_t2',
            'mdm1_t2',
            'msd1_t2'],
 'creodron': ['gfr1_t2',
              'gbc2_t2',
              'gf5_t2',
              'gf4_t2a',
              'gc3_t2',
              'gb1_t2',
              'gdh1_t2',
              'gdl1_t2',
              'gdm1_t2',
              'gsd1_t2'],
 'development': ['oref1_t2b'],
 'duvolle': ['gc1_t2a',
             'gbc1_t2a',
             'gc4_t2a',
             'gf7_t2',
             'gb2_t2',
             'gf3_t2',
             'gf6_t2b',
             'gi4_t2'],
 'ishukone': ['cf3_t2',
              'cc2_t2b',
              'cc4_t2a',
              'cf7_t2b',
              'cfr1_t2',
              'cbc1_t2b'],
 'kaalakiota': ['ci2_t2',
                'cf2_t2a',
                'cde1_t2',
                'cbc2_t2',
                'cc2_t2a',
                'cc4_t2b',
                'cb2_t2'],
 'khanid': ['af7_t2',
            'ac1_t2a',
            'abc1_t2a',
            'ade1_t2',
            'ai1_t2',
            'af4_t2a',
            'ac2_t2a',
            'af3_t2a'],
 'laidai': ['cc1_t2',
            'ci3_t2',
            'cc3_t2',
            'cb1_t2',
            'cf7_t2a',
            'cf4_t2',
            'cf6_t2',
            'cf2_t2b',
            'cdh1_t2',
            'cdl1_t2',
            'cdm1_t2',
            'csd1_t2'],
 'orebase': ['oredh1_t2'],
 'prospecting': ['oreba3_t2', 'oreba2_t2', 'oreba1_t2'],
 'roden': ['gf6_t2a',
           'gf4_t2b',
           'gde1_t2',
           'gc1_t2b',
           'gi2_t2',
           'gc2_t2',
           'gc4_t2b'],
 'sarum': ['abc_t2',
           'afr1_t2',
           'af4_t2b',
           'ac3_t2',
           'ab1_t2',
           'ac1_t2b',
           'af3_t2b',
           'adh1_t2',
           'adl1_t2',
           'adm1_t2',
           'asd1_t2'],
 'sebiestor': ['mc2_t2c',
               'mi3_t2c',
               'mc3_t2c',
               'mde1_t2c',
               'mc4_t2c',
               'mf1_t2c'],
 'thukker': ['mf2_t2b',
             'mf4_t2b',
             'mi2_t2b',
             'mfr1_t2',
             'mb1_t2b',
             'mc1_t2b']}

class SOFPreviewWindow:

    def __init__(self):
        self.name = 'SOF Preview Window'
        self.windowID = 'SOFPreviewWindow_ ' + self.name
        self.previewCont = None
        dna = self.GetDnaFromPlayerShip()
        self.currentHull = dna.split(':')[0]
        self.currentFaction = dna.split(':')[1]
        self.currentRace = dna.split(':')[2]
        self.currentMat = ['None',
         'None',
         'None',
         'None']
        self.currentDirtLevel = None
        self.currentResPathInsert = None
        self.constrainToFaction = False
        self.constrainToHull = False
        self.constrainToRace = False

    def _OnApplyButton(self, *args):
        self._UpdatePlayerShip()

    def ShowUI(self):
        uicontrols.Window.CloseIfOpen(windowID=self.windowID)
        wnd = uicontrols.Window.Open(windowID=self.windowID)
        wnd.SetTopparentHeight(0)
        wnd.SetMinSize([500, 500])
        wnd.SetCaption(self.name)
        main = wnd.GetMainArea()
        sofDB = blue.resMan.LoadObject('res:/dx9/model/spaceobjectfactory/data.red')
        self.sofFactions = []
        for i in xrange(len(sofDB.faction)):
            self.sofFactions.append((sofDB.faction[i].name, i))

        self.sofFactions.sort()
        self.sofHulls = []
        for i in xrange(len(sofDB.hull)):
            self.sofHulls.append((sofDB.hull[i].name, i))

        self.sofHulls.sort()
        self.sofRaces = []
        for i in xrange(len(sofDB.race)):
            self.sofRaces.append((sofDB.race[i].name, i))

        self.sofRaces.sort()
        self.sofMaterials = []
        for i in xrange(len(sofDB.material)):
            self.sofMaterials.append((sofDB.material[i].name, i))

        self.sofMaterials.sort()
        self.sofMaterials.insert(0, ('None', -1))
        headerCont = Container(name='headerCont', parent=main, align=uiconst.TOTOP, height=30)
        gridCont = GridContainer(name='mainCont', parent=main, align=uiconst.TOBOTTOM, height=250, lines=5, columns=3)
        buttonConts = {}
        for y in xrange(gridCont.lines):
            for x in xrange(gridCont.columns):
                buttonConts[x, y] = Container(parent=gridCont)

        self.dnaLabel = EveLabelSmall(name='dnaLabel', align=uiconst.CENTER, parent=headerCont, text='')
        self.applyButton = Button(name='apply_button', align=uiconst.CENTER, parent=buttonConts[(1, 4)], label='Apply', func=self._OnApplyButton)
        factionParent = Container(name='factionParent', parent=buttonConts[(0, 2)], align=uiconst.CENTER, height=18, width=175)
        self.factionCombo = Combo(name='faction_combo', align=uiconst.TOLEFT, width=150, parent=factionParent, label='Faction:', options=self.sofFactions, callback=self.OnFactionComboChange, select=self.GetComboListIndex(self.sofFactions, self.currentFaction))
        self.factionConstraint = Checkbox(name='faction_constraint', align=uiconst.TOLEFT, width=75, padLeft=10, parent=factionParent, text='Constrained', callback=self.OnFactionConstraintChanged)
        hullParent = Container(name='hullParent', parent=buttonConts[(0, 1)], align=uiconst.CENTER, height=18, width=175)
        self.hullCombo = Combo(name='hull_combo', align=uiconst.TOLEFT, width=150, parent=hullParent, label='Hull:', options=self.sofHulls, callback=self.OnHullComboChange, select=self.GetComboListIndex(self.sofHulls, self.currentHull))
        self.hullConstraint = Checkbox(name='hull_constraint', align=uiconst.TOLEFT, width=75, padLeft=10, parent=hullParent, text='Constrained', callback=self.OnHullConstraintChanged)
        raceParent = Container(name='raceParent', parent=buttonConts[(0, 0)], align=uiconst.CENTER, height=18, width=175)
        self.raceCombo = Combo(name='race_combo', align=uiconst.TOLEFT, width=150, parent=raceParent, label='Race:', options=self.sofRaces, callback=self.OnRaceComboChange, select=self.GetComboListIndex(self.sofRaces, self.currentRace))
        self.raceConstraint = Checkbox(name='race_constraint', align=uiconst.TOLEFT, width=75, padLeft=10, parent=raceParent, text='Constrained', callback=self.OnRaceConstraintChanged)
        self.matCombo1 = Combo(name='material_combo1', align=uiconst.CENTER, width=150, parent=buttonConts[(1, 0)], label='Material 1:', options=self.sofMaterials, callback=self.OnMat1ComboChange, select=self.GetComboListIndex(self.sofMaterials, self.currentMat[0]))
        self.matCombo2 = Combo(name='material_combo2', align=uiconst.CENTER, width=150, parent=buttonConts[(1, 1)], label='Material 2:', options=self.sofMaterials, callback=self.OnMat2ComboChange, select=self.GetComboListIndex(self.sofMaterials, self.currentMat[1]))
        self.matCombo3 = Combo(name='material_combo3', align=uiconst.CENTER, width=150, parent=buttonConts[(1, 2)], label='Material 3:', options=self.sofMaterials, callback=self.OnMat3ComboChange, select=self.GetComboListIndex(self.sofMaterials, self.currentMat[2]))
        self.matCombo4 = Combo(name='material_combo4', align=uiconst.CENTER, width=150, parent=buttonConts[(1, 3)], label='Material 4:', options=self.sofMaterials, callback=self.OnMat4ComboChange, select=self.GetComboListIndex(self.sofMaterials, self.currentMat[3]))
        self.dirtSlider = Slider(name='dirt_slider', align=uiconst.CENTER, label='Dirt', parent=buttonConts[(2, 0)], width=200, minValue=0.0, maxValue=100.0, startVal=50.0, setlabelfunc=self.UpdateDirtSliderLabel, onsetvaluefunc=self.OnDirtSliderChange, endsliderfunc=self.OnDirtSliderChange)
        self.materialSetIDEdit = SinglelineEdit(name='materialsetid_edit', align=uiconst.CENTER, label='Masterial Set ID', parent=buttonConts[(2, 1)], width=100, setvalue='', OnFocusLost=self.OnMaterialSetIDChange, OnReturn=self.OnMaterialSetIDChange)
        self.resPathInsertEdit = SinglelineEdit(name='respathinsert_edit', align=uiconst.CENTER, label='resPathInsert', parent=buttonConts[(2, 2)], width=100, setvalue='', OnFocusLost=self.OnResPathInsertChange, OnReturn=self.OnResPathInsertChange)
        self.previewCont = PreviewContainer(parent=main, align=uiconst.TOALL)
        self.previewCont.PreviewSofDna(self.GetPreviewDna())

    def GetComboListIndex(self, comboContentList, name):
        for each in comboContentList:
            if each[0].lower() == name.lower():
                return each[1]

    def GetPreviewDna(self):
        dna = self.currentHull + ':' + self.currentFaction + ':' + self.currentRace
        if any((x != 'None' for x in self.currentMat)):
            dna += ':mesh?' + str(self.currentMat[0]) + ';' + str(self.currentMat[1]) + ';' + str(self.currentMat[2]) + ';' + str(self.currentMat[3])
        if self.currentResPathInsert is not None:
            dna += ':respathinsert?' + str(self.currentResPathInsert)
        self.dnaLabel.text = dna
        return dna

    def GetDnaFromPlayerShip(self):
        michelle = sm.GetService('michelle')
        ship = michelle.GetBall(session.shipid)
        if ship is None:
            return 'ab1_t1:amarrbase:amarr'
        return ship.GetDNA()

    def UpdateDirtSliderLabel(self, label, sliderID, displayName, value):
        dirtLevel = gfxutils.RemapDirtLevel(value)
        label.text = 'Dirt level: ' + str(dirtLevel)

    def OnDirtSliderChange(self, slider):
        self.currentDirtLevel = gfxutils.RemapDirtLevel(slider.GetValue())
        self._UpdatePreviewShip()

    def OnFactionConstraintChanged(self, checkbox):
        self.constrainToFaction = checkbox.GetValue()
        self.ConstrainDnaSelection()

    def OnRaceConstraintChanged(self, checkbox):
        self.constrainToRace = checkbox.GetValue()
        self.ConstrainDnaSelection()

    def OnHullConstraintChanged(self, checkbox):
        self.constrainToHull = checkbox.GetValue()
        self.ConstrainDnaSelection()

    def ConstrainDnaSelection(self):
        raceQuery = '.*'
        factionQuery = '.*'
        hullQuery = '.*'
        if self.constrainToFaction:
            factionQuery = self.factionCombo.GetKey()
        if self.constrainToHull:
            hullQuery = self.hullCombo.GetKey()
        if self.constrainToRace:
            raceQuery = self.raceCombo.GetKey()
        if not self.constrainToFaction and not self.constrainToHull and not self.constrainToRace:
            self.currentFaction = self.TrySettingComboOptions(self.factionCombo, self.sofFactions, self.GetDefaultFactionForHull())
            self.currentRace = self.TrySettingComboOptions(self.raceCombo, self.sofRaces, self.currentRace)
            self.currentHull = self.TrySettingComboOptions(self.hullCombo, self.sofHulls, self.currentHull)
        else:
            dnaList = GetDnaStringMatchingQuery(hullQuery, factionQuery, raceQuery)
            selectableRaces = []
            selectableFactions = []
            selectableHulls = []
            for dna in dnaList:
                dnaElements = dna.split(':')
                hull = dnaElements[0]
                faction = dnaElements[1]
                race = dnaElements[2]
                if faction not in selectableFactions:
                    selectableFactions.append(faction)
                if race not in selectableRaces:
                    selectableRaces.append(race)
                if hull not in selectableHulls:
                    selectableHulls.append(hull)

            if not self.constrainToHull:
                selectableHulls.sort()
                hullOptions = [ (hullName, i) for i, hullName in enumerate(selectableHulls) ]
                self.currentHull = self.TrySettingComboOptions(self.hullCombo, hullOptions, self.currentHull)
            if not self.constrainToFaction:
                selectableFactions.sort()
                options = [ (factionName, i) for i, factionName in enumerate(selectableFactions) ]
                self.currentFaction = self.TrySettingComboOptions(self.factionCombo, options, self.GetDefaultFactionForHull())
            if not self.constrainToRace:
                selectableRaces.sort()
                raceOptions = [ (raceName, i) for i, raceName in enumerate(selectableRaces) ]
                self.currentRace = self.TrySettingComboOptions(self.raceCombo, raceOptions, self.currentRace)
        self._UpdatePreviewShip()

    def GetDefaultFactionForHull(self):
        if self.currentHull.endswith('t2'):
            return self._GetDefaultFactionForT2Hull(self.currentHull)
        else:
            return self._GetDefaultFactionForT1Hull(self.currentHull)

    @staticmethod
    def _GetDefaultFactionForT1Hull(hullName):
        dnaList = GetDnaStringMatchingQuery(hullName)
        if len(dnaList) == 0:
            return ''
        _, __, race = dnaList[0].split(':')
        return race + 'base'

    @staticmethod
    def _GetDefaultFactionForT2Hull(hullName):
        for factionName, hullList in DEFAULT_FACTION_FOR_T2HULLS.iteritems():
            if hullName in hullList:
                return factionName

        return ''

    def TrySettingComboOptions(self, comboBox, options, selectedValue):
        comboBox.LoadOptions(options)
        return self.TrySettingComboValue(comboBox, selectedValue)

    def TrySettingComboValue(self, comboBox, selectedValue):
        try:
            comboBox.SelectItemByLabel(selectedValue)
        except RuntimeError:
            comboBox.SelectItemByIndex(0)
            print "Could not select '%s', defaulting to '%s'" % (selectedValue, comboBox.GetKey())

        return comboBox.GetKey()

    def OnFactionComboChange(self, comboBox, faction, value):
        self.currentFaction = faction
        if self.constrainToFaction:
            self.ConstrainDnaSelection()
        self._UpdatePreviewShip()

    def OnHullComboChange(self, comboBox, hull, value):
        self.currentHull = hull
        if self.constrainToHull:
            self.ConstrainDnaSelection()
        self._UpdatePreviewShip()

    def OnRaceComboChange(self, comboBox, race, value):
        self.currentRace = race
        if self.constrainToRace:
            self.ConstrainDnaSelection()
        self._UpdatePreviewShip()

    def OnMat1ComboChange(self, comboBox, material, value):
        self.currentMat[0] = material
        self._UpdatePreviewShip()

    def OnMat2ComboChange(self, comboBox, material, value):
        self.currentMat[1] = material
        self._UpdatePreviewShip()

    def OnMat3ComboChange(self, comboBox, material, value):
        self.currentMat[2] = material
        self._UpdatePreviewShip()

    def OnMat4ComboChange(self, comboBox, material, value):
        self.currentMat[3] = material
        self._UpdatePreviewShip()

    def OnMaterialSetIDChange(self, *args):
        materialSetID = int(self.materialSetIDEdit.GetValue())
        print 'trying to find materialset for ' + str(materialSetID)
        materialSet = cfg.graphicMaterialSets.GetIfExists(materialSetID)
        if hasattr(materialSet, 'sofFactionName'):
            idx = self.GetComboListIndex(self.sofFactions, materialSet.sofFactionName)
            self.factionCombo.SelectItemByValue(idx)
            self.OnFactionComboChange(self.factionCombo, materialSet.sofFactionName, idx)
        if hasattr(materialSet, 'material1'):
            idx = self.GetComboListIndex(self.sofMaterials, materialSet.material1)
            self.matCombo1.SelectItemByValue(idx)
            self.OnMat1ComboChange(self.matCombo1, materialSet.material1, idx)
        if hasattr(materialSet, 'material2'):
            idx = self.GetComboListIndex(self.sofMaterials, materialSet.material2)
            self.matCombo2.SelectItemByValue(idx)
            self.OnMat2ComboChange(self.matCombo2, materialSet.material2, idx)
        if hasattr(materialSet, 'material3'):
            idx = self.GetComboListIndex(self.sofMaterials, materialSet.material3)
            self.matCombo3.SelectItemByValue(idx)
            self.OnMat3ComboChange(self.matCombo3, materialSet.material3, idx)
        if hasattr(materialSet, 'material4'):
            idx = self.GetComboListIndex(self.sofMaterials, materialSet.material4)
            self.matCombo4.SelectItemByValue(idx)
            self.OnMat4ComboChange(self.matCombo4, materialSet.material4, idx)
        if hasattr(materialSet, 'resPathInsert'):
            self.resPathInsertEdit.SetValue(materialSet.resPathInsert)
            self.OnResPathInsertChange()

    def OnResPathInsertChange(self, *args):
        resPathInsert = self.resPathInsertEdit.GetValue()
        print 'new respathinsert: ' + resPathInsert
        if len(resPathInsert) == 0:
            self.currentResPathInsert = None
        else:
            self.currentResPathInsert = resPathInsert
        self._UpdatePreviewShip()

    def _UpdatePreviewShip(self):
        if self.previewCont is not None:
            self.previewCont.PreviewSofDna(self.GetPreviewDna(), dirt=self.currentDirtLevel)

    def _UpdatePlayerShip(self):
        michelle = sm.GetService('michelle')
        ship = michelle.GetBall(session.shipid)
        if ship is None:
            return
        ship.UnfitHardpoints()
        ship.Release()
        while ship.model is not None:
            blue.synchro.Yield()

        ship.released = False
        ship.GetDNA = self.GetPreviewDna
        ship.LoadModel()
        ship.Assemble()
        if self.currentDirtLevel is not None:
            ship.model.dirtLevel = self.currentDirtLevel
