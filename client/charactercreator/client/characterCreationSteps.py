#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\charactercreator\client\characterCreationSteps.py
import charactercreator.const as ccConst

def GetStepsForMode(mode):
    stepToMode = {ccConst.MODE_FULL_BLOODLINECHANGE: [ccConst.RACESTEP,
                                         ccConst.BLOODLINESTEP,
                                         ccConst.CUSTOMIZATIONSTEP,
                                         ccConst.PORTRAITSTEP,
                                         ccConst.NAMINGSTEP],
     ccConst.MODE_FULL_RECUSTOMIZATION: [ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP],
     ccConst.MODE_LIMITED_RECUSTOMIZATION: [ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP],
     ccConst.MODE_FULLINITIAL_CUSTOMIZATION: [ccConst.RACESTEP,
                                              ccConst.BLOODLINESTEP,
                                              ccConst.CUSTOMIZATIONSTEP,
                                              ccConst.PORTRAITSTEP,
                                              ccConst.NAMINGSTEP],
     ccConst.MODE_INITIAL_MINI_CUSTOMIZATION: [ccConst.RACESTEP, ccConst.BLOODLINESTEP, ccConst.MINIMALNAMINGSTEP]}
    return stepToMode[mode]


class Mode(object):

    def __init__(self, modeID, canChangeBaseAppearance = False, canChangeName = False, canChangeGender = False, canChangeBloodline = False, willExitToStation = True, askPortraitInfo = False, isInitialCreation = False, limited = False, useOldPortraitData = False):
        self.modeID = modeID
        self.canChangeName = canChangeName
        self.canChangeGender = canChangeGender
        self.canChangeBaseAppearance = canChangeBaseAppearance
        self.canChangeBloodline = canChangeBloodline
        self.willExitToStation = willExitToStation
        self.askForPortraitConfirmation = askPortraitInfo
        self.isInitialCreation = isInitialCreation
        self.limitedHelpText = limited
        self.useOldPortraitData = useOldPortraitData
        self.steps = {}

    def GetValue(self):
        return ccConst.MODE_FULL_BLOODLINECHANGE

    def GetSteps(self):
        return GetStepsForMode(self.modeID)

    def CanChangeBaseAppearance(self):
        return self.canChangeBaseAppearance

    def CanChangeGender(self):
        return self.canChangeGender

    def CanChangeName(self):
        return self.canChangeName

    def CanChangeBloodLine(self):
        return self.canChangeBloodline

    def AskForPortraitConfirmation(self):
        return self.askForPortraitConfirmation

    def ExitToStation(self):
        return self.willExitToStation

    def IsInitialCreation(self):
        return self.isInitialCreation

    def IsLimited(self):
        return self.limitedHelpText

    def GetOldPortraitData(self):
        return self.useOldPortraitData


class ModeStorage(object):

    def __init__(self):
        self.modes = {}
        fullInitialCustomization = Mode(modeID=ccConst.MODE_FULLINITIAL_CUSTOMIZATION, canChangeBaseAppearance=True, canChangeBloodline=True, canChangeName=True, canChangeGender=True, willExitToStation=False)
        fullBloodlineChange = Mode(modeID=ccConst.MODE_FULL_BLOODLINECHANGE, canChangeBloodline=True, canChangeGender=False, canChangeBaseAppearance=False)
        fullRecustomization = Mode(modeID=ccConst.MODE_FULL_RECUSTOMIZATION, canChangeBaseAppearance=True, askPortraitInfo=True, useOldPortraitData=True)
        limitedRecustomization = Mode(modeID=ccConst.MODE_LIMITED_RECUSTOMIZATION, canChangeBaseAppearance=False, askPortraitInfo=True, limited=1, useOldPortraitData=True, willExitToStation=True)
        miniInitialCustomization = Mode(modeID=ccConst.MODE_INITIAL_MINI_CUSTOMIZATION, canChangeBaseAppearance=True, canChangeBloodline=True, canChangeName=True, canChangeGender=True, willExitToStation=False, askPortraitInfo=True, useOldPortraitData=False)
        self.modes[ccConst.MODE_FULLINITIAL_CUSTOMIZATION] = fullInitialCustomization
        self.modes[ccConst.MODE_FULL_BLOODLINECHANGE] = fullBloodlineChange
        self.modes[ccConst.MODE_FULL_RECUSTOMIZATION] = fullRecustomization
        self.modes[ccConst.MODE_LIMITED_RECUSTOMIZATION] = limitedRecustomization
        self.modes[ccConst.MODE_INITIAL_MINI_CUSTOMIZATION] = miniInitialCustomization

    def GetModeFor(self, modeID):
        return self.modes[modeID]
