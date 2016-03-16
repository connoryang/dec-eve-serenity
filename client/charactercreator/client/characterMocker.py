#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\charactercreator\client\characterMocker.py
import random
import carbon.common.lib.telemetry as telemetry
import eve.client.script.ui.login.charcreation.ccUtil as ccUtil
import eve.common.script.paperDoll.paperDollDefinitions as pdDef
import charactercreator.const as ccConst
from utillib import KeyVal
from eve.client.script.ui.login.charcreation.eveDollRandomizer import EveDollRandomizer
from charactercreator.client.characterDollUtilities import CharacterDollUtilities

class EveAvatarAndClothesRandomizer:

    def __init__(self):
        factory = sm.GetService('character').factory
        self.loader = factory
        self.randomizer = EveDollRandomizer(self.loader)
        self.cachedDoll = None
        self.metadata = None
        self.randomizationInProgress = False

    def InitializeDollAndMetadata(self, genderID, bloodline):
        randomizer = self.randomizer
        if genderID is not None:
            genderString = ccUtil.GenderIDToPaperDollGender(genderID)
            randomizer.gender = genderString
        if bloodline is not None:
            randomizer.bloodline = bloodline
        randomizer.SetSculptingLimits()
        doll = randomizer.GetDoll(True, None)
        self.cachedDoll = doll
        self.metadata = self.GetNewCharacterMetadata()

    def GetGender(self):
        return self.randomizer.gender

    def GetGenderID(self):
        return ccUtil.PaperDollGenderToGenderID(self.GetGender())

    def GetBloodline(self):
        return self.randomizer.bloodline

    def GetNewCharacterMetadata(self):
        return KeyVal(genderID=ccUtil.PaperDollGenderToGenderID(self.GetGender()), bloodlineID=self.GetBloodline(), types={}, typeColors={}, typeWeights={}, typeSpecularity={}, hairDarkness=0.0)

    def GetRandomOptions(self):
        return self.randomizer.GetBlendshapeOptions()

    def GetMetadata(self):
        return self.metadata

    def GetDollFactory(self):
        return self.loader

    def RandomizeSculpts(self):
        options = self.randomizer.GetBlendshapeOptions()
        return self.ApplyRandomizedResourcesToCharacter(options)

    def ApplyRandomizedResourcesToCharacter(self, randomizedResources):
        dollFactory = self.GetDollFactory()
        MASTER_COLORS = [ccConst.hair, ccConst.eyes]
        dollUtilities = CharacterDollUtilities()
        bloodLine = self.GetBloodline()
        gender = self.GetGender()
        colorProvider = sm.GetService('character')
        doll = self.cachedDoll
        metadata = self.GetMetadata()
        modifiers = []
        genderID = ccUtil.PaperDollGenderToGenderID(gender)
        for cat, categoryValue in randomizedResources.iteritems():
            for resType, res in categoryValue:
                if not res:
                    continue
                var = None
                weight = self.randomizer.weights.get(res, 1.0)
                if resType == self.randomizer.RESOURCE_TYPE:
                    resPath = self.loader.GetItemType(res, gender=gender)[0]
                    color1Value, color1Name, color2Name, variation = (None, None, None, None)
                    glossiness = None
                    colorizeData = None
                    if cat in MASTER_COLORS or cat.startswith('makeup') and cat != 'makeup/eyebrows' or cat.startswith('tattoo'):
                        colorsA, colorsB = colorProvider.GetAvailableColorsForCategory(cat, genderID, bloodLine)
                        colorA = []
                        colorB = []
                        if len(colorsA) > 0:
                            colorA = random.choice(colorsA)
                            colorB = None
                            if len(colorsB) > 0:
                                colorB = random.choice(colorsB)
                            color1Value, color1Name, color2Name, variation = colorProvider.GetColorsToUse(colorA, colorB)
                        if color1Value:
                            colorizeData = color1Value
                        elif colorB or variation:
                            var = variation
                        elif len(colorA) > 0:
                            var = colorA[1]
                        if gender == pdDef.GENDER.FEMALE and ccUtil.HasUserDefinedSpecularity(cat):
                            glossiness = round(0.3 + 0.3 * random.random(), 2)
                    if color1Name:
                        metadata.typeColors[cat] = (color1Name, color2Name)
                    if glossiness:
                        dollUtilities.SetColorSpecularityByCategory(doll, cat, glossiness, doUpdate=False, metadata=metadata)
                    modifier = dollUtilities.ApplyTypeToDoll(res, weight, doUpdate=False, rawColorVariation=var, metadata=metadata, factory=dollFactory, doll=doll)
                    if colorizeData:
                        modifier.SetColorizeData(colorizeData)
                else:
                    from eve.common.script.paperDoll.paperDollRandomizer import AbstractRandomizer
                    modifier = dollUtilities.ApplyItemToDoll(cat, res, removeFirst=True, doUpdate=False, doll=doll, metadata=metadata, factory=dollFactory)
                    colorVariations = self.randomizer.GetColorVariations(modifier)
                    colorVariation = AbstractRandomizer.SelectOneFromCollection(colorVariations, oddsOfSelectingNone=0)
                    if colorVariation:
                        colorTuple = (colorVariation, modifier.colorVariations[colorVariation])
                        dollUtilities.SetColorValueByCategory(doll, metadata, cat, colorTuple, None, doUpdate=False)
                    modifier.weight = weight
                modifiers.append(modifier)

        return metadata

    def RandomizeDollCategory(self, category, oddsOfSelectingNone, addWeight = None, weightFrom = 0, weightTo = 1.0, fullRandomization = False):
        randomizer = EveDollRandomizer(self.loader)
        randomizer.gender = self.GetGender()
        randomizer.bloodline = self.GetBloodline()
        randomizer.fullRandomization = fullRandomization
        randomizer.AddCategoryForWhitelistRandomization(category, oddsOfSelectingNone)
        if addWeight:
            randomizer.AddPathForWeightRandomization(category, weightFrom, weightTo)
        options = randomizer.GetResources()
        self.ApplyRandomizedResourcesToCharacter(options)

    def GetCharacterApperanceInfo(self):
        import paperDoll
        dollDNA = self.cachedDoll.GetDNA()
        return paperDoll.ConvertDNAForDB(dollDNA, self.GetMetadata())

    @telemetry.ZONE_METHOD
    def RandomizeWholeDoll(self):
        self.RandomizeSculpts()
        self.RandomizeClothes()

    def RandomizeClothes(self):
        items = self.getRandomizedItemsForGender(self.GetGender())
        from charactercreator.client.characterDollUtilities import CharacterDollUtilities
        dollUtilities = CharacterDollUtilities()
        dollUtilities.RandomizeCharacterGroups(self.cachedDoll, categoryList=items, doUpdate=False, fullRandomization=True, metadata=self.GetMetadata(), factory=self.loader, randomizeCategoryCallback=self.RandomizeDollCategory)

    def getRandomizedItemsForGender(self, gender):
        if gender == ccConst.GENDERID_FEMALE:
            itemList = ccConst.femaleRandomizeItems.keys()
        else:
            itemList = ccConst.maleRandomizeItems.keys()
        return itemList
