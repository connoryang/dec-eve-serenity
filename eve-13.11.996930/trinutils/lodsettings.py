#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinutils\lodsettings.py
import sys
import trinity
KEY_LOWDETAIL = 'eveSpaceSceneLowDetailThreshold'
KEY_MEDDETAIL = 'eveSpaceSceneMediumDetailThreshold'
HIGH = (0, 0)
MEDIUM = (0, sys.maxint)
LOW = (sys.maxint, sys.maxint)
_settings = trinity.settings
DEFAULT = (_settings.GetValue(KEY_LOWDETAIL), _settings.GetValue(KEY_MEDDETAIL))

def View(threshold):
    _settings.SetValue(KEY_LOWDETAIL, threshold[0])
    _settings.SetValue(KEY_MEDDETAIL, threshold[1])
