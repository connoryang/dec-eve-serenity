#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\radialMenu\radialMenuUtils.py
import util

class SimpleRadialMenuAction(util.KeyVal):

    def __init__(self, option1 = None, option2 = None, *args, **kw):
        self.option1Path = option1
        self.option2Path = option2
        self.activeOption = option1
        self.func = None
        self.funcArgs = ()
        for attrname, val in kw.iteritems():
            setattr(self, attrname, val)


class RangeRadialMenuAction(util.KeyVal):

    def __init__(self, optionPath = None, optionPath2 = None, rangeList = None, defaultRange = None, callback = None, *args, **kw):
        self.option1Path = optionPath
        self.option2Path = optionPath2
        self.activeOption = optionPath
        self.rangeList = rangeList
        self.defaultRange = defaultRange
        self.callback = callback
        for attrname, val in kw.iteritems():
            setattr(self, attrname, val)


class SecondLevelRadialMenuAction(util.KeyVal):

    def __init__(self, levelType = '', texturePath = 'res:/UI/Texture/classes/RadialMenu/plus.png', *args, **kw):
        self.option1Path = ''
        self.activeOption = ''
        self.levelType = levelType
        self.texturePath = texturePath
        for attrname, val in kw.iteritems():
            setattr(self, attrname, val)


class RadialMenuOptionsInfo:

    def __init__(self, allWantedMenuOptions, activeSingleOptions = None, inactiveSingleOptions = None, activeRangeOptions = None, inactiveRangeOptions = None):
        self.allWantedMenuOptions = allWantedMenuOptions
        self.activeSingleOptions = activeSingleOptions or {}
        self.inactiveSingleOptions = inactiveSingleOptions or set()
        self.activeRangeOptions = activeRangeOptions or {}
        self.inactiveRangeOptions = inactiveRangeOptions or set()


def FindOptionsDegree(counter, degreeStep, startingDegree = 0, alternate = False):
    if counter == 0:
        return startingDegree
    if alternate:
        rightSide = counter % 2
        numOnSide = counter / 2
        if rightSide:
            numOnSide += 1
        degree = numOnSide * degreeStep
        if not rightSide:
            degree = -degree + 360
    else:
        degree = counter * degreeStep
    degree = startingDegree + degree
    if degree >= 360:
        degree -= 360
    return degree


class RadialMenuSizeInfo:

    def __init__(self, width, height, shadowSize, rangeSize, sliceCount, buttonHeight, buttonWidth, buttonPaddingTop, buttonPaddingBottom, actionDistance):
        self.width = width
        self.height = height
        self.shadowSize = shadowSize
        self.rangeSize = rangeSize
        self.sliceCount = sliceCount
        self.buttonHeight = buttonHeight
        self.buttonWidth = buttonWidth
        self.buttonPaddingTop = buttonPaddingTop
        self.buttonPaddingBottom = buttonPaddingBottom
        self.actionDistance = actionDistance
