#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\graphics\device.py
import trinity

def SetEnvMipLevelSkipCount():
    trinity.device.mipLevelSkipCount = 0


def SetCharMipLevelSkipCount():
    trinity.device.mipLevelSkipCount = 0


exports = {'device.SetEnvMipLevelSkipCount': SetEnvMipLevelSkipCount,
 'device.SetCharMipLevelSkipCount': SetCharMipLevelSkipCount}
