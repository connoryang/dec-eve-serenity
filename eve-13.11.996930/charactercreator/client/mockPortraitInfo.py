#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\charactercreator\client\mockPortraitInfo.py
from utillib import KeyVal

class PortraitInfo:

    @staticmethod
    def getDictionaryObject():
        portraitInfo = {}
        portraitInfo['backgroundID'] = 14
        portraitInfo['cache'] = []
        portraitInfo['cacheTime'] = 0
        portraitInfo['cameraFieldOfView'] = 0.3
        portraitInfo['cameraPoi'] = (0.00983966700732708, 1.6130555868148804, 0.07999974489212036)
        portraitInfo['cameraPosition'] = (0.00983966700732708, 1.6130555868148804, 1.3981997966766357)
        portraitInfo['lightColorID'] = 10866
        portraitInfo['lightID'] = 10866
        portraitInfo['lightIntensity'] = 0.5
        portraitInfo['minutes'] = 0
        poseData = {'BrowLeftCurl': 0.5,
         'BrowLeftTighten': 0.0,
         'BrowLeftUpDown': 0.5,
         'BrowRightCurl': 0.5,
         'BrowRightTighten': 0.0,
         'BrowRightUpDown': 0.5,
         'EyeClose': 0.0,
         'EyesLookHorizontal': 0.5,
         'EyesLookVertical': 0.5,
         'FrownLeft': 0.0,
         'FrownRight': 0.0,
         'HeadLookTarget': (0.0, 1.5, 1.0),
         'HeadTilt': 0.0,
         'JawSideways': 0.5,
         'JawUp': 0.5,
         'OrientChar': 0.5,
         'PortraitPoseNumber': 4.0,
         'PuckerLips': 0.5,
         'SmileLeft': 0.5,
         'SmileRight': 0.5,
         'SquintLeft': 0.5,
         'SquintRight': 0.5}
        portraitInfo['poseData'] = poseData
        return portraitInfo

    @staticmethod
    def getMockyData():
        return KeyVal(PortraitInfo.getDictionaryObject())
