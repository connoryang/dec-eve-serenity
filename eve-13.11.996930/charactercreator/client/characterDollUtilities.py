#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\charactercreator\client\characterDollUtilities.py
import charactercreator.const as ccConst
from utillib import KeyVal
import eve.common.lib.appConst as const
import paperDoll

class CharacterDollUtilities:

    def __init__(self):
        self.modifierLocationsByName = {}
        self.modifierLocationsByKey = {}
        self.assetsToIDs = {'male': None,
         'female': None}

    def GetNewCharacterMetadata(self, genderID, bloodlineID):
        return KeyVal(genderID=genderID, bloodlineID=bloodlineID, types={}, typeColors={}, typeWeights={}, typeSpecularity={}, hairDarkness=0.0)

    def RemoveFromCharacterMetadata(self, metadata, category):
        if category in metadata.types:
            metadata.types.pop(category, None)
            metadata.typeColors.pop(category, None)
            metadata.typeSpecularity.pop(category, None)
            metadata.typeWeights.pop(category, None)

    def SetColorSpecularityByCategory(self, doll, category, specularity, doUpdate = True, metadata = None):
        modifier = self.GetModifierByCategory(doll, category)
        if modifier:
            metadata.typeSpecularity[category] = specularity
            m1 = 1.0 + 0.4 * specularity
            s1 = 0.5 + 0.3 * specularity
            s2 = 0.5 - 0.2 * specularity
            modifier.SetColorVariationSpecularity([(s1,
              s1,
              s1,
              m1), (s2,
              s2,
              s2,
              1.0), (0.5, 0.5, 0.5, 1.0)])

    def GetModifierByCategory(self, doll, category, getAll = False):
        modifiers = self.GetModifiersByCategory(doll, category)
        if not modifiers:
            return None
        elif getAll:
            return modifiers
        else:
            if category == paperDoll.HAIR_CATEGORIES.BEARD:
                for modifier in modifiers:
                    if modifier.name != 'stubble':
                        return modifier

            return modifiers[0]

    def GetModifiersByCategory(self, doll, category):
        ret = []
        mods = doll.buildDataManager.GetModifiersAsList(includeFuture=True)
        for m in mods:
            resPath = m.GetResPath()
            resPathSplit = resPath.split('/')
            categSplit = category.split('/')
            match = True
            for i, each in enumerate(categSplit):
                if not (len(resPathSplit) > i and resPathSplit[i] == each):
                    match = False
                    break

            if match:
                ret.append(m)

        return ret

    def ApplyTypeToDoll(self, itemType, weight = 1.0, doUpdate = True, rawColorVariation = None, metadata = None, factory = None, doll = None):
        if itemType is None:
            return
        import eve.client.script.ui.login.charcreation.ccUtil as ccUtil
        self.PopulateModifierLocationDicts()
        genderID = metadata.genderID
        if type(itemType) is not tuple:
            charGender = ccUtil.GenderIDToPaperDollGender(genderID)
            itemTypeData = factory.GetItemType(itemType, gender=charGender)
            if itemTypeData is None:
                itemTypeLower = itemType.lower()
                if paperDoll.BODY_CATEGORIES.TOPINNER in itemTypeLower:
                    self.ApplyItemToDoll(paperDoll.BODY_CATEGORIES.TOPINNER, None, removeFirst=True, doUpdate=False, doll=doll, metadata=metadata, factory=factory)
                elif paperDoll.BODY_CATEGORIES.BOTTOMINNER in itemTypeLower:
                    self.ApplyItemToDoll(paperDoll.BODY_CATEGORIES.BOTTOMINNER, None, removeFirst=True, doUpdate=False, doll=doll, metadata=metadata, factory=factory)
                else:
                    print "Item type file is missing, can't be loaded %s" % str(itemType)
                return
            assetID, assetTypeID = self.GetAssetAndTypeIDsFromPath(charGender, itemType)
            itemType = (assetID, itemTypeData[:3], assetTypeID)
        category = self.GetCategoryFromResPath(itemType[1][0])
        godmaSvc = sm.GetService('godma')
        modifierLocationKey = self.modifierLocationsByName.get(category, None)
        toRemove = []
        for otherCategory, otherResourceID in metadata.types.iteritems():
            if otherResourceID is None:
                continue
            otherResource = cfg.paperdollResources.Get(otherResourceID)
            if otherResource.typeID is None:
                continue
            removesCategory = godmaSvc.GetTypeAttribute2(otherResource.typeID, const.attributeClothingRemovesCategory)
            if removesCategory == modifierLocationKey:
                toRemove.append(otherCategory)

        for itemToRemove in toRemove:
            self.ApplyItemToDoll(itemToRemove, None, removeFirst=True, doUpdate=False)

        activeMod = self.GetModifierByCategory(doll, category)
        if activeMod:
            doll.RemoveResource(activeMod.GetResPath(), factory)
        modifier = doll.AddItemType(factory, itemType[1], weight, rawColorVariation)
        metadata.types[category] = itemType[0]
        myTypeID = itemType[2]
        if myTypeID:
            removesCategory = godmaSvc.GetTypeAttribute2(myTypeID, const.attributeClothingRemovesCategory)
            if removesCategory:
                modifierLocationName = self.modifierLocationsByKey[int(removesCategory)]
                self.ApplyItemToDoll(modifierLocationName, None, removeFirst=True, doUpdate=False, doll=doll, metadata=metadata, factory=factory)
        if ccUtil.HasUserDefinedWeight(category):
            metadata.typeWeights[category] = weight
        if category in (ccConst.hair, ccConst.beard, ccConst.eyebrows):
            self.SynchronizeHairColors(metadata, doll)
        return modifier

    def PopulateModifierLocationDicts(self, force = False):
        if not force and len(self.modifierLocationsByKey) > 0:
            return
        self.modifierLocationsByName = {}
        self.modifierLocationsByKey = {}
        for row in cfg.paperdollModifierLocations:
            self.modifierLocationsByKey[row.modifierLocationID] = row.modifierKey
            self.modifierLocationsByName[row.modifierKey] = row.modifierLocationID

    def ApplyItemToDoll(self, category, name, removeFirst = False, variation = None, doUpdate = True, doll = None, metadata = None, factory = None):
        modifier = None
        modifierFoundForVariationSwitch = False
        if name and variation:
            modifier = self.GetModifierByCategory(doll, category)
            if modifier and modifier.name.split(paperDoll.SEPERATOR_CHAR)[-1] == name:
                modifier.SetVariation(variation)
                modifierFoundForVariationSwitch = True
        if not modifierFoundForVariationSwitch:
            if removeFirst:
                if name:
                    modifier = self.GetModifierByCategory(doll, category)
                    if modifier:
                        self.RemoveFromCharacterMetadata(metadata, category)
                        doll.RemoveResource(modifier.respath, factory)
                else:
                    modifiers = self.GetModifierByCategory(doll, category, getAll=True)
                    if modifiers:
                        self.RemoveFromCharacterMetadata(metadata, category)
                        for modifier in modifiers:
                            doll.RemoveResource(modifier.respath, factory)

            if name:
                modifier = doll.AddResource(category + '/' + name, 1.0, factory, variation=variation)
            elif not removeFirst:
                modifier = self.GetModifierByCategory(doll, category)
                if modifier:
                    self.RemoveFromCharacterMetadata(metadata, category)
                    doll.RemoveResource(modifier.GetResPath(), factory)
        return modifier

    def SynchronizeHairColors(self, metadata, doll):
        import geo2
        hairData = self.GetModifierByCategory(doll, ccConst.hair)
        if hairData is not None:
            colorizeData = hairData.colorizeData
            orgA, orgB, orgC = colorizeData
            newA = geo2.Vector(*orgA)
            lowA = newA * 0.2
            newA = geo2.Vec4Lerp(lowA, newA, metadata.hairDarkness)
            adjustedColor = (newA, orgB, orgC)
            for hairModifier in (ccConst.beard, ccConst.eyebrows):
                if hairModifier == ccConst.beard:
                    hms = self.GetModifierByCategory(doll, hairModifier, getAll=True)
                else:
                    hms = [self.GetModifierByCategory(doll, hairModifier)]
                if hms is None:
                    continue
                for hm in hms:
                    if hm:
                        hm.colorizeData = adjustedColor
                        hm.pattern = hairData.pattern
                        hm.patternData = hairData.patternData
                        hm.specularColorData = hairData.specularColorData
                        hm.SetColorVariation('none')

    def SetColorValueByCategory(self, doll, metadata, category, colorVar1, colorVar2, doUpdate = True):
        if colorVar1 is None:
            return
        color1Value, color1Name, color2Name, variation = self.GetColorsToUse(colorVar1, colorVar2)
        modifier = self.GetModifierByCategory(doll, category)
        if not modifier:
            return
        if color1Value:
            metadata.typeColors[category] = (color1Name, None)
            modifier.SetColorizeData(color1Value)
        elif colorVar2 is not None:
            metadata.typeColors[category] = (color1Name, color2Name)
            modifier.SetColorVariationDirectly(variation)
        else:
            metadata.typeColors[category] = (color1Name, None)
            modifier.SetColorVariationDirectly(variation)
        if category == ccConst.hair:
            self.SynchronizeHairColors(metadata, doll)

    def GetColorsToUse(self, colorVar1, colorVar2, *args):
        if colorVar1 is None:
            return (None, None, None, None)
        if len(colorVar1) == 3:
            colorVar1 = (colorVar1[0], colorVar1[2])
        if colorVar2 is not None and len(colorVar2) == 3:
            colorVar2 = (colorVar2[0], colorVar2[2])
        color1Name, color1Value = colorVar1
        import types
        if type(color1Value) == types.TupleType:
            return (color1Value,
             color1Name,
             None,
             None)
        elif colorVar2 is not None:
            color2Name, color2Value = colorVar2
            variation = {}
            if color1Value:
                if color2Value and 'colors' in color1Value:
                    variation['colors'] = [color1Value['colors'][0], color2Value['colors'][1], color2Value['colors'][2]]
                if 'pattern' in color1Value:
                    variation['pattern'] = color1Value['pattern']
                if color2Value and 'patternColors' in color1Value:
                    variation['patternColors'] = [color1Value['patternColors'][0], color2Value['patternColors'][1], color2Value['patternColors'][2]]
                if 'patternColors' in color1Value:
                    variation['patternColors'] = color1Value['patternColors']
                if color2Value and 'specularColors' in color1Value:
                    variation['specularColors'] = [color1Value['specularColors'][0], color2Value['specularColors'][1], color2Value['specularColors'][2]]
            return (None,
             color1Name,
             color2Name,
             variation)
        else:
            return (None,
             color1Name,
             None,
             color1Value)

    def GetAssetAndTypeIDsFromPath(self, gender, assetPath):
        if self.assetsToIDs[gender] is None:
            self.assetsToIDs[gender] = {}
            for row in cfg.paperdollResources:
                if row.resGender == (gender == paperDoll.GENDER.MALE):
                    self.assetsToIDs[gender][self.GetRelativePath(row.resPath).lower()] = (row.paperdollResourceID, row.typeID)

        assetPath = self.GetRelativePath(assetPath).lower()
        if assetPath in self.assetsToIDs[gender]:
            return self.assetsToIDs[gender][assetPath]
        else:
            print 'Asset ID %s does not have an associated ID!!' % assetPath
            return (None, None)

    def RandomizeCharacterGroups(self, doll, categoryList, doUpdate = False, fullRandomization = False, metadata = None, factory = None, randomizeCategoryCallback = None):
        doHairDarkness = False
        for category in categoryList:
            if category in (ccConst.hair, ccConst.beard, ccConst.eyebrows):
                doHairDarkness = True
            addWeight = False
            weightFrom = 0.1
            if fullRandomization and category.startswith('makeup/'):
                weightTo = 0.3
            else:
                weightTo = 1.0
            modifier = self.GetModifierByCategory(doll, category)
            if modifier:
                self.RemoveFromCharacterMetadata(metadata, category)
                doll.RemoveResource(modifier.GetResPath(), factory)
            if category in ccConst.addWeightToCategories:
                addWeight = True
            oddsDict = {}
            if doll.gender == 'female':
                oddsDict = ccConst.femaleOddsOfSelectingNone.copy()
                if fullRandomization:
                    oddsDict.update(ccConst.femaleOddsOfSelectingNoneFullRandomize)
            else:
                oddsDict = ccConst.maleOddsOfSelectingNone.copy()
                if fullRandomization:
                    oddsDict.update(ccConst.maleOddsOfSelectingNoneFullRandomize)
            oddsOfSelectingNone = oddsDict.get(category, None)
            randomizeCategoryCallback(category, oddsOfSelectingNone, addWeight, weightFrom, weightTo, fullRandomization)

    def RandomizeDollCategory(self, charID, category, oddsOfSelectingNone, addWeight = None, weightFrom = 0, weightTo = 1.0, fullRandomization = False):
        randomizer = paperDoll.EveDollRandomizer(self.factory)
        randomizer.gender = self.characters[charID].doll.gender
        randomizer.bloodline = self.characterMetadata[charID].bloodlineID
        randomizer.fullRandomization = fullRandomization
        randomizer.AddCategoryForWhitelistRandomization(category, oddsOfSelectingNone)
        if addWeight:
            randomizer.AddPathForWeightRandomization(category, weightFrom, weightTo)
        options = randomizer.GetResources()
        randomizer.ApplyRandomizedResourcesToCharacter(charID, options)

    def GetRelativePath(self, resPath):
        if resPath.lower().startswith('res:'):
            for chopPart in ['Modular/Female/',
             'Modular/Male/',
             'Female/Paperdoll/',
             'Male/Paperdoll/',
             'modular/female/',
             'modular/male/',
             'female/paperdoll/',
             'male/paperdoll/']:
                startPos = resPath.find(chopPart)
                if startPos != -1:
                    chopTo = len(chopPart) + startPos
                    resPath = resPath[chopTo:]

        return resPath

    def GetCategoryFromResPath(self, resPath):
        parts = resPath.split('/')
        return '/'.join(parts[:-1])
