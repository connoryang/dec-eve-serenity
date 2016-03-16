#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveaudio\shiphealthnotification.py
from brennivin import itertoolsext
from eve.common.lib.appConst import soundNotifications

class SoundNotification(object):

    def __init__(self, keyName):
        if isinstance(keyName, int):
            index = keyName
            namesToIndices = soundNotifications.get('NameToIndices')
            keyName = itertoolsext.first([ k for k, v in namesToIndices.items() if v == index ])
        notification = soundNotifications.get(keyName)
        self.activeFlagSettingsName = keyName + 'NotificationEnabled'
        self.healthThresholdSettingsName = keyName + 'Threshold'
        self.defaultThreshold = notification.get('defaultThreshold')
        self.notificationEventName = notification.get('soundEventName')
        self.localizationLabel = notification.get('localizationLabel')
        self.defaultStatus = notification.get('defaultStatus')
        self.hasBeenNotified = False
        self.name = keyName


class ShipSoundNotifications(object):

    def __init__(self):
        self.shield = SoundNotification('shield')
        self.armour = SoundNotification('armour')
        self.hull = SoundNotification('hull')
        self.capacitor = SoundNotification('capacitor')
        self.cargoHold = SoundNotification('cargoHold')


class ShipHealthNotifier(object):

    def __init__(self, sendEvent, setRTPC):
        self.soundNotifications = ShipSoundNotifications()
        self.sendEvent = sendEvent
        self.setGlobalRTPC = setRTPC

    def OnDamageStateChange(self, shipID, damageState):
        if session.shipid != shipID:
            return
        self.ProcessNotification(self.soundNotifications.shield, damageState[0])
        self.ProcessNotification(self.soundNotifications.armour, damageState[1])
        self.ProcessNotification(self.soundNotifications.hull, damageState[2])
        self.UpdateGlobalRTPCShipHealthLevels(damageState)

    def OnCapacitorChange(self, currentCharge, maxCharge, percentageLoaded):
        self.ProcessNotification(self.soundNotifications.capacitor, percentageLoaded)

    def OnCargoHoldChange(self, shipID, cargoHoldState, item, change):
        if cargoHoldState.capacity == 0:
            return
        if shipID in item or shipID in change.values():
            cargoHoldFree = cargoHoldState.capacity - cargoHoldState.used
            percentageUsed = cargoHoldFree / cargoHoldState.capacity
            self.ProcessNotification(self.soundNotifications.cargoHold, percentageUsed)

    def ProcessNotification(self, soundNotification, currentDamageStateValue):
        enabled = settings.user.notifications.Get(soundNotification.activeFlagSettingsName, True)
        if not enabled:
            return
        damageStateThreshold = settings.user.notifications.Get(soundNotification.healthThresholdSettingsName, soundNotification.defaultThreshold)
        thresholdReached = currentDamageStateValue <= damageStateThreshold
        self._SendNotificationIfNeeded(soundNotification, thresholdReached)

    def _SendNotificationIfNeeded(self, soundNotification, thresholdReached):
        alreadyNotified = soundNotification.hasBeenNotified
        if thresholdReached and not alreadyNotified:
            self.sendEvent(soundNotification.notificationEventName)
            soundNotification.hasBeenNotified = True
        elif alreadyNotified:
            soundNotification.hasBeenNotified = thresholdReached

    def UpdateGlobalRTPCShipHealthLevels(self, damageState):
        rtpcNames = ['ship_health_shield', 'ship_health_armour', 'ship_health_hull']
        for i in xrange(3):
            self.setGlobalRTPC(rtpcNames[i], damageState[i] * 100.0)
