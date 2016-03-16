#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\steps\characterCustomization.py
from carbonui import const as uiconst
from charactercreator import const as ccConst
from eve.client.script.ui.login.charcreation import ccUtil
from eve.client.script.ui.login.charcreation.charCreation import BaseCharacterCreationStep, MAXMENUSIZE
from evegraphics import settings as gfxsettings
import localization
import service
import uicls
import uicontrols
import uiprimitives
import uthread
import blue

class CharacterCustomization(BaseCharacterCreationStep):
    __guid__ = 'uicls.CharacterCustomization'
    __notifyevents__ = ['OnColorPaletteChanged', 'OnHideUI', 'OnShowUI']
    stepID = ccConst.CUSTOMIZATIONSTEP
    ASSETMENU = 1
    TATTOOMENU = 2

    def ApplyAttributes(self, attributes):
        uicore.event.RegisterForTriuiEvents(uiconst.UI_ACTIVE, self.CheckAppFocus)
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        info = self.GetInfo()
        self.menuMode = self.ASSETMENU
        self.charID = attributes.charID
        self.colorPaletteWidth = uicls.CCColorPalette.COLORPALETTEWIDTH
        self.tattooChangeMade = 0
        self.menusInitialized = 0
        self.sr.leftSide.width = 200
        self.sr.headBodyPicker = uicls.CCHeadBodyPicker(name='headBodyPicker', parent=self.sr.leftSide, align=uiconst.CENTERTOP, top=98, headCallback=self.LoadFaceMode, bodyCallback=self.LoadBodyMode)
        clickable = uicore.layer.charactercreation.CanChangeBloodline()
        if clickable and not uicore.layer.charactercreation.CanChangeGender():
            disabledHex = ['gender']
        else:
            disabledHex = []
        picker = uicls.CCRacePicker(parent=self.sr.uiContainer, align=uiconst.BOTTOMLEFT, raceID=info.raceID, bloodlineID=info.bloodlineID, genderID=info.genderID, padding=(30, 0, 0, -8), clickable=clickable, disabledHex=disabledHex)
        self.sr.assetMenuPar = uiprimitives.Container(parent=self.sr.rightSide, name='assetMenuPar', pos=(0,
         0,
         MAXMENUSIZE,
         uicore.desktop.height), state=uiconst.UI_PICKCHILDREN, align=uiconst.CENTERTOP)
        self.sr.hintBox = uiprimitives.Container(parent=self.sr.assetMenuPar, pos=(0, 20, 200, 150), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED)
        self.sr.hintText = uicontrols.EveLabelMedium(text='', parent=self.sr.hintBox, align=uiconst.TOTOP)
        self.sr.randomButton = uiprimitives.Transform(parent=self.sr.headBodyPicker, pos=(-52, 34, 22, 22), state=uiconst.UI_NORMAL, align=uiconst.CENTERTOP, hint=localization.GetByLabel('UI/CharacterCreation/RandomizeAll'), idx=0)
        self.sr.randomButton.OnClick = self.RandomizeCharacter
        self.sr.randomButton.OnMouseEnter = (self.OnGenericMouseEnter, self.sr.randomButton)
        self.sr.randomButton.OnMouseExit = (self.OnGenericMouseExit, self.sr.randomButton)
        randIcon = uicontrols.Icon(parent=self.sr.randomButton, icon=ccConst.ICON_RANDOM, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=ccConst.COLOR50)
        self.sr.randomButton.sr.icon = randIcon
        self.sr.toggleClothesButton = uiprimitives.Container(parent=self.sr.headBodyPicker, pos=(52, 32, 26, 26), state=uiconst.UI_NORMAL, align=uiconst.CENTERTOP, hint=localization.GetByLabel('UI/CharacterCreation/ToggleClothes'), idx=0)
        toggleIcon = uicontrols.Icon(parent=self.sr.toggleClothesButton, icon=ccConst.ICON_TOGGLECLOTHES, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=ccConst.COLOR50)
        self.sr.toggleClothesButton.OnClick = self.ToggleClothes
        self.sr.toggleClothesButton.OnMouseEnter = (self.OnGenericMouseEnter, self.sr.toggleClothesButton)
        self.sr.toggleClothesButton.OnMouseExit = (self.OnGenericMouseExit, self.sr.toggleClothesButton)
        self.sr.toggleClothesButton.sr.icon = toggleIcon
        self.UpdateLayout()
        self.StartLoadingThread()

    def StartLoadingThread(self, *args):
        if self.sr.loadingWheelThread:
            self.sr.loadingWheelThread.kill()
            self.sr.loadingWheelThread = None
        self.sr.loadingWheelThread = uthread.new(self.ShowLoadingWheel_thread)

    def SetHintText(self, modifier, hintText = ''):
        text = hintText
        if modifier in ccConst.HELPTEXTS:
            labelPath = ccConst.HELPTEXTS[modifier]
            text = localization.GetByLabel(labelPath)
        elif modifier == ccConst.eyes:
            labelPath = ccConst.HELPTEXTS[ccConst.EYESGROUP]
            text = localization.GetByLabel(labelPath)
        if text != self.sr.hintText.text:
            self.sr.hintText.text = text

    def ToggleClothes(self, *args):
        if uicore.layer.charactercreation.doll.busyUpdating:
            raise UserError('uiwarning01')
        uicore.layer.charactercreation.ToggleClothes()

    def OnGenderSelected(self, genderID):
        self.GoToAssetMode(animate=0, forcedMode=1)
        if self.sr.tattooMenu:
            self.sr.tattooMenu.Close()

    def UpdateLayout(self, *args):
        BaseCharacterCreationStep.UpdateLayout(self)
        self.colorPaletteWidth = uicls.CCColorPalette.COLORPALETTEWIDTH
        self.sr.assetMenuPar.height = uicore.desktop.height
        for menu in (self.sr.tattooMenu, self.sr.assetMenu):
            if menu and not menu.destroyed:
                menu.ChangeHeight(self.sr.assetMenuPar.height)

        self.sr.rightSide.width += self.colorPaletteWidth
        sm.GetService('cc').LogInfo('CharacterCustomization::UpdateLayout')
        if not self.menusInitialized:
            self.sr.tattooMenu = self.ReloadTattooMenu()
            self.sr.assetMenu = self.ReloadAssetMenu()
            self.menusInitialized = 1
        self.LoadMenu()

    def OnColorPaletteChanged(self, width, *args):
        if width > self.colorPaletteWidth:
            difference = width - self.colorPaletteWidth
            self.colorPaletteWidth = width
            self.sr.rightSide.width += difference
            self.sr.assetMenu.width += difference
            self.sr.assetMenuPar.width += difference
            self.sr.hintBox.left = self.assetMenuMainWidth + 20

    def RandomizeCharacter(self, randomizingPart = None, *args):
        info = self.GetInfo()
        doll = self.charSvc.GetSingleCharactersDoll(info.charID)
        if doll.busyUpdating:
            return
        uicore.layer.charactercreation.LockNavigation()
        uicore.layer.charactercreation.ToggleClothes(forcedValue=0)
        uthread.new(self.RandomizeRotation_thread, self.sr.randomButton)
        itemList = []
        if info.genderID == ccConst.GENDERID_FEMALE:
            itemList = ccConst.femaleRandomizeItems.keys()
        else:
            itemList = ccConst.maleRandomizeItems.keys()
        canChangeBaseAppearance = uicore.layer.charactercreation.CanChangeBaseAppearance()
        blacklist = ccConst.randomizerCategoryBlacklist[:]
        if not canChangeBaseAppearance:
            blacklist += ccConst.recustomizationRandomizerBlacklist
        if info.genderID == ccConst.GENDERID_FEMALE:
            blacklist.append(ccConst.scarring)
        categoryList = []
        for item in itemList:
            if item not in blacklist:
                categoryList.append(item)

        self.charSvc.RandomizeCharacterGroups(info.charID, categoryList, doUpdate=False, fullRandomization=True)
        if canChangeBaseAppearance:
            self.charSvc.RandomizeCharacterSculpting(info.charID, doUpdate=False)
        decalModifiers = doll.buildDataManager.GetModifiersByCategory(ccConst.tattoo)
        for modifier in decalModifiers:
            modifier.IsDirty = True

        self.charSvc.UpdateDoll(info.charID, 'RandomizeCharacter')

    def RandomizeRotation_thread(self, randomButton, *args):
        randomButton.StartRotationCycle(cycleTime=750.0, cycles=5)
        if randomButton and not randomButton.destroyed:
            randomButton.SetRotation(0)

    def LoadMenu(self, animate = 0, forcedMode = 0, *arg):
        sm.GetService('cc').LogInfo('CharacterCustomization::LoadMenu')
        menu = None
        if self.menuMode == self.ASSETMENU:
            menu = self.GetAssetMenu(forcedMode)
        elif self.menuMode == self.TATTOOMENU:
            menu = self.GetTattooMenu(forcedMode)
        if menu is None:
            return
        if animate:
            mainCont = menu.sr.mainCont
            if self.menuMode == self.TATTOOMENU:
                fullHeight = menu.sr.mainCont.height
                mainCont.height = menu.sr.menuToggler.height
                menu.state = uiconst.UI_DISABLED
                uicore.effect.MorphUIMassSpringDamper(mainCont, 'height', fullHeight, newthread=False, float=False, frequency=15.0, dampRatio=0.85)
                menu.state = uiconst.UI_PICKCHILDREN
            else:
                menu.state = uiconst.UI_DISABLED
                uicore.effect.MorphUIMassSpringDamper(mainCont, 'top', 0, newthread=False, float=False, frequency=15.0, dampRatio=0.85)
                menu.sr.mainCont.height = uicore.desktop.height
                menu.state = uiconst.UI_PICKCHILDREN
        else:
            menu.state = uiconst.UI_PICKCHILDREN
        menu.CheckIfOversize()

    def GetTattooMenu(self, forcedMode = 0, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::GetTattooMenu')
        if not forcedMode and self.sr.tattooMenu and not self.sr.tattooMenu.destroyed:
            if self.sr.assetMenu:
                self.sr.assetMenu.state = uiconst.UI_HIDDEN
            self.sr.tattooMenu.sr.mainCont.top = 0
            return self.sr.tattooMenu
        else:
            return self.ReloadTattooMenu()

    def ReloadTattooMenu(self, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::ReloadTattooMenu')
        self.StartLoadingThread()
        if self.sr.assetMenu:
            self.sr.assetMenu.state = uiconst.UI_HIDDEN
        if self.sr.tattooMenu:
            self.sr.tattooMenu.Close()
        info = self.GetInfo()
        piercingSub = (ccConst.p_brow,
         ccConst.p_nose,
         ccConst.p_nostril,
         ccConst.p_earshigh,
         ccConst.p_earslow,
         ccConst.p_lips,
         ccConst.p_chin)
        scarSub = (ccConst.s_head,)
        tattooSub = (ccConst.t_head, ccConst.t_armleft, ccConst.t_armright)
        prostheticsSub = (ccConst.pr_armleft, ccConst.pr_armright)
        groups = []
        groups += [(ccConst.PIERCINGGROUP, piercingSub)]
        groups += [(ccConst.TATTOOGROUP, tattooSub)]
        groups += [(ccConst.SCARSGROUP, scarSub)]
        groups += [(ccConst.PROSTHETICS, prostheticsSub)]
        tattoooMenuWidth = min(MAXMENUSIZE + uicls.CCColorPalette.COLORPALETTEWIDTH, self.sr.rightSide.width - 32)
        self.sr.tattooMenu = uicls.CharCreationAssetMenu(menuType='tattooMenu', parent=self.sr.assetMenuPar, bloodlineID=info.bloodlineID, state=uiconst.UI_PICKCHILDREN, genderID=info.genderID, charID=info.charID, groups=groups, align=uiconst.CENTERTOP, width=tattoooMenuWidth, height=uicore.desktop.height, top=16, toggleFunc=self.GoToAssetMode, togglerIdx=0)
        self.sr.tattooMenu.width = tattoooMenuWidth
        return self.sr.tattooMenu

    def GetAssetMenu(self, forcedMode = 0, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::GetAssetMenu')
        if not forcedMode and self.sr.assetMenu and not self.sr.assetMenu.destroyed:
            if self.sr.tattooMenu and not self.sr.tattooMenu.destroyed:
                self.sr.tattooMenu.state = uiconst.UI_HIDDEN
                self.sr.tattooMenu.sr.mainCont.height = uicore.desktop.height - self.sr.tattooMenu.top
            return self.sr.assetMenu
        else:
            return self.ReloadAssetMenu()

    def ReloadAssetMenu(self, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::ReloadAssetMenu')
        self.StartLoadingThread()
        if self.sr.assetMenu:
            self.sr.assetMenu.Close()
        if self.sr.tattooMenu:
            self.sr.tattooMenu.state = uiconst.UI_HIDDEN
        info = self.GetInfo()
        makeup = ccConst.MAKEUPGROUP
        if info.genderID == 1:
            makeup = ccConst.SKINDETAILSGROUP
        clothesSub = (ccConst.outer,
         ccConst.topouter,
         ccConst.topmiddle,
         ccConst.bottomouter,
         ccConst.bottommiddle,
         ccConst.feet,
         ccConst.glasses)
        groups = []
        if uicore.layer.charactercreation.CanChangeBaseAppearance():
            groups += [(ccConst.BODYGROUP, ())]
            groups += [(ccConst.SKINGROUP, ())]
        groups += [(ccConst.EYESGROUP, ())]
        groups += [(ccConst.HAIRGROUP, ())]
        groups += [(makeup, (ccConst.eyeshadow,
           ccConst.eyeliner,
           ccConst.blush,
           ccConst.lipstick))]
        groups += [(ccConst.CLOTHESGROUP, clothesSub)]
        assetMenuWidth = min(MAXMENUSIZE + uicls.CCColorPalette.COLORPALETTEWIDTH, self.sr.rightSide.width - 32)
        self.assetMenuMainWidth = assetMenuWidth - uicls.CCColorPalette.COLORPALETTEWIDTH
        self.sr.assetMenu = uicls.CharCreationAssetMenu(menuType='assetMenu', parent=self.sr.assetMenuPar, bloodlineID=info.bloodlineID, state=uiconst.UI_PICKCHILDREN, genderID=info.genderID, charID=info.charID, groups=groups, align=uiconst.CENTERTOP, width=assetMenuWidth, height=uicore.desktop.height, top=16, toggleFunc=self.GoToTattooMode)
        self.sr.assetMenuPar.width = assetMenuWidth
        if self.sr.historySlider:
            self.sr.historySlider.Close()
        self.sr.historySlider = uicls.CharacterCreationHistorySlider(parent=self.sr.uiContainer, align=uiconst.CENTERBOTTOM, top=-32, width=500, opacity=0.0, bitChangeCheck=self.IsDollReady, lastLitHistoryBit=uicore.layer.charactercreation.lastLitHistoryBit)
        self.sr.hintBox.left = self.assetMenuMainWidth + 20
        mask = service.ROLE_CONTENT | service.ROLE_QA | service.ROLE_PROGRAMMER | service.ROLE_GMH
        if eve.session.role & mask:
            if self.sr.debugReloadBtn:
                self.sr.debugReloadBtn.Close()
                self.sr.tattooModeBtn.Close()
                self.sr.typeAddEdit.Close()
                self.sr.validationToggle.Close()
                self.sr.typeAddBtn.Close()
            self.sr.debugReloadBtn = uicontrols.Button(parent=self.sr.uiContainer, func=self.GoToAssetMode, args=(0, 1), label='Reload Menu (debug)', align=uiconst.TOPRIGHT, left=self.sr.randomButton.left + 30, top=16)
            self.sr.tattooModeBtn = uicontrols.Button(parent=self.sr.uiContainer, func=self.GoToTattooMode, args=(0, 1), label='Go to Tattoo mode (debug)', align=uiconst.TOPRIGHT, left=250, top=16)
            self.sr.typeAddEdit = uicontrols.SinglelineEdit(parent=self.sr.uiContainer, name='typeAdd', ints=(0, 100000), align=uiconst.TOPRIGHT, left=650, top=16, maxLength=10)
            self.sr.validationToggle = uicontrols.Button(parent=self.sr.uiContainer, name='validationToggle', func=self.ToggleValidation, label='Validation On', align=uiconst.TOPRIGHT, left=430, top=16)
            self.sr.typeAddBtn = uicontrols.Button(parent=self.sr.uiContainer, func=self.AddTypeButton, label='Add Type (debug)', align=uiconst.TOPRIGHT, left=530, top=16)
            self.sr.addBlankDoll = uicontrols.Button(parent=self.sr.uiContainer, func=self.AddBlankDrifterDoll, label='Add Blank Drifter Doll (debug)', align=uiconst.TOPRIGHT, left=530, top=35)
        uthread.new(uicore.effect.CombineEffects, self.sr.historySlider, top=42, opacity=1.0, time=125.0)
        return self.sr.assetMenu

    def AddBlankDrifterDoll(self, *args):
        import paperDoll
        info = self.GetInfo()
        self.charSvc.RemoveCharacter(info.charID)
        self.charSvc.AddCharacterToScene(info.charID, uicore.layer.charactercreation.scene, ccUtil.GenderIDToPaperDollGender(info.genderID), bloodlineID=19, noRandomize=True, updateDoll=False)
        doll = uicore.layer.charactercreation.doll = self.charSvc.GetSingleCharactersDoll(info.charID)
        while doll.IsBusyUpdating():
            blue.synchro.Yield()

        doll.overrideLod = paperDoll.LOD_SKIN
        textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
        doll.textureResolution = ccConst.TEXTURE_RESOLUTIONS[textureQuality]
        if uicore.layer.charactercreation.IsSlowMachine():
            doll.useFastShader = True
        else:
            doll.useFastShader = False
        self.charSvc.SetDollBloodline(info.charID, 19)
        self.charSvc.UpdateDoll(info.charID, fromWhere='AddCharacter')

    def ToggleValidation(self, *args):
        validating = sm.RemoteSvc('charUnboundMgr').ToggleValidation()
        if validating:
            self.sr.validationToggle.SetLabel('Validation On')
        else:
            self.sr.validationToggle.SetLabel('Validation Off')

    def AddTypeButton(self, *args):
        resourceID = self.sr.typeAddEdit.GetValue()
        paperdollResource = cfg.paperdollResources.Get(resourceID)
        if paperdollResource:
            info = self.GetInfo()
            itemRelativeResPath = self.charSvc.GetRelativePath(paperdollResource.resPath).lower()
            itemTypeData = self.charSvc.factory.GetItemType(itemRelativeResPath, gender=ccUtil.GenderIDToPaperDollGender(info.genderID))
            itemInfo = (resourceID, itemTypeData[:3], paperdollResource.typeID)
            uicore.layer.charactercreation.SetItemType(itemInfo)

    def GoToTattooMode(self, animate = 1, forcedMode = 0, *args):
        if not sm.StartService('device').SupportsSM3():
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/CharacterCreation/BodyModificationsNeedSM3')})
            return
        self.menuMode = self.TATTOOMENU
        self.tattooChangeMade = 0
        self.charSvc.StopEditing()
        if self.sr.historySlider:
            self.sr.historySlider.state = uiconst.UI_HIDDEN
        self.sr.randomButton.Disable()
        if self.sr.assetMenu and not self.sr.assetMenu.destroyed:
            mainCont = self.sr.assetMenu.sr.mainCont
            h = mainCont.height - self.sr.assetMenu.sr.menuToggler.padTop
            h = mainCont.height - self.sr.assetMenu.sr.menuToggler.height - 4
            uicore.effect.MorphUIMassSpringDamper(mainCont, 'top', -h, newthread=False, float=False, frequency=15.0, dampRatio=0.85)
        self.LoadMenu(animate=animate, forcedMode=forcedMode)

    def GoToAssetMode(self, animate = 1, forcedMode = 0, *args):
        self.menuMode = self.ASSETMENU
        if self.sr.tattooMenu and not self.sr.tattooMenu.destroyed:
            if self.tattooChangeMade:
                uicore.layer.charactercreation.TryStoreDna(False, 'GoToAssetMode', sculpting=False, force=1, allowReduntant=0)
            mainCont = self.sr.tattooMenu.sr.mainCont
            h = self.sr.tattooMenu.sr.menuToggler.height + self.sr.tattooMenu.sr.menuToggler.padTop + self.sr.tattooMenu.sr.menuToggler.padBottom
            uicore.effect.CombineEffects(mainCont, height=h, time=250.0)
            uicore.effect.CombineEffects(mainCont, top=-8, time=10.0)
        self.tattooChangeMade = 0
        if uicore.layer.charactercreation.CanChangeBaseAppearance():
            uicore.layer.charactercreation.StartEditMode()
        if self.sr.historySlider:
            self.sr.historySlider.state = uiconst.UI_PICKCHILDREN
        self.sr.randomButton.Enable()
        self.LoadMenu(animate=1, forcedMode=forcedMode)

    def OnGenericMouseEnter(self, btn, *args):
        btn.sr.icon.SetAlpha(1.0)

    def OnGenericMouseExit(self, btn, *args):
        btn.sr.icon.SetAlpha(0.5)

    def LoadFaceMode(self, *args):
        info = self.GetInfo()
        avatar = self.charSvc.GetSingleCharactersAvatar(info.charID)
        uicore.layer.charactercreation.camera.ToggleMode(ccConst.CAMERA_MODE_FACE, avatar=avatar, transformTime=500.0)

    def LoadBodyMode(self, *args):
        info = self.GetInfo()
        avatar = self.charSvc.GetSingleCharactersAvatar(info.charID)
        uicore.layer.charactercreation.camera.ToggleMode(ccConst.CAMERA_MODE_BODY, avatar=avatar, transformTime=500.0)

    def ValidateStepComplete(self):
        info = self.GetInfo()
        if prefs.GetValue('ignoreCCValidation', False):
            return True
        if self.menuMode == self.TATTOOMENU:
            uicore.layer.charactercreation.TryStoreDna(False, 'ValidateStepComplete', force=1, allowReduntant=0)
        while not self.IsDollReady():
            blue.synchro.Yield()

        return self.charSvc.ValidateDollCustomizationComplete(info.charID)

    def ShowLoadingWheel_thread(self, *args):
        layer = uicore.layer.charactercreation
        doll = layer.doll
        while doll and not self.destroyed:
            if layer.sr.step and getattr(layer.sr.step, '_activeSculptZone', None) is not None:
                layer.HideLoading()
            elif doll.busyUpdating:
                layer.ShowLoading(why=localization.GetByLabel('UI/CharacterCreation/UpdatingCharacter'))
            else:
                layer.HideLoading()
            blue.pyos.synchro.SleepWallclock(100)

    def CheckAppFocus(self, wnd, msgID, vkey):
        focused = vkey[0]
        if not focused:
            uicore.layer.charactercreation.PassMouseEventToSculpt('LeftDown', uicore.uilib.x, uicore.uilib.y)
            uicore.layer.charactercreation.PassMouseEventToSculpt('LeftUp', uicore.uilib.x, uicore.uilib.y)
            self.ChangeSculptingCursor(-1, 0, 0)
            uicore.layer.charactercreation.UnfreezeAnimationIfNeeded()
        return 1

    def StoreHistorySliderPosition(self, *args):
        if self.sr.historySlider:
            currentIndex, maxIndex = self.sr.historySlider.GetCurrentIndexAndMaxIndex()
        else:
            currentIndex = None
        uicore.layer.charactercreation.lastLitHistoryBit = currentIndex
