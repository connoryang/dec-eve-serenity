#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\notifySettingsWindow.py
from carbonui import const as uiconst
from eve.common.lib.appConst import soundNotifications
from eveaudio.shiphealthnotification import SoundNotification
import localization
import uicontrols
import uiprimitives

class NotifySettingsWindow(uicontrols.Window):
    default_windowID = 'NotifySettingsWindow'
    default_fixedHeight = 190
    default_fixedWidth = 380

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon(None)
        self.SetTopparentHeight(0)
        self.SetCaption(localization.GetByLabel('UI/Inflight/NotifySettingsWindow/DamageAlertSettings'))
        self.MakeUnResizeable()
        self.SetupUi()

    def SetupUi(self):
        self.notifydata = []
        notificationList = ['shield',
         'armour',
         'hull',
         'capacitor',
         'cargoHold']
        for name in notificationList:
            notification = SoundNotification(name)
            data = {'checkboxLabel': localization.GetByLabel(notification.localizationLabel),
             'checkboxName': name + 'Notification',
             'checkboxSetting': notification.activeFlagSettingsName,
             'checkboxDefault': notification.defaultStatus,
             'sliderName': name,
             'sliderSetting': (name + 'Threshold', ('user', 'notifications'), notification.defaultThreshold)}
            self.notifydata.append(data)

        labelWidth = 180
        mainContainer = uiprimitives.Container(name='mainContainer', parent=self.sr.main, align=uiconst.TOALL)
        for each in self.notifydata:
            name = each['sliderName']
            notifytop = uiprimitives.Container(name='notifytop', parent=mainContainer, align=uiconst.TOTOP, pos=(const.defaultPadding,
             const.defaultPadding,
             0,
             32))
            uicontrols.Checkbox(text=each['checkboxLabel'], parent=notifytop, configName=each['checkboxSetting'], retval=None, prefstype=('user', 'notifications'), checked=settings.user.notifications.Get(each['checkboxSetting'], each['checkboxDefault']), callback=self.CheckBoxChange, align=uiconst.TOLEFT, pos=(const.defaultPadding,
             0,
             labelWidth,
             0))
            _par = uiprimitives.Container(name=name + '_slider', align=uiconst.TORIGHT, width=labelWidth, parent=notifytop, pos=(10, 0, 160, 0))
            par = uiprimitives.Container(name=name + '_slider_sub', align=uiconst.TOTOP, parent=_par, pos=(0,
             const.defaultPadding,
             0,
             10))
            slider = uicontrols.Slider(parent=par, gethintfunc=self.GetSliderHint, endsliderfunc=self.SliderChange)
            slider.Startup(name, 0.0, 1.0, each['sliderSetting'])

    def GetSliderHint(self, idname, dname, value):
        return localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=value * 100)

    def SliderChange(self, slider):
        if slider.name == 'shieldThreshold':
            uicore.layer.shipui.sr.shipAlertContainer.AlertThresholdChanged('shield')
        elif slider.name == 'armourThreshold':
            uicore.layer.shipui.sr.shipAlertContainer.AlertThresholdChanged('armour')
        elif slider.name == 'hullThreshold':
            uicore.layer.shipui.sr.shipAlertContainer.AlertThresholdChanged('hull')
        elif slider.name == 'capacitorThreshold':
            uicore.layer.shipui.sr.shipAlertContainer.AlertThresholdChanged('capacitor')
        elif slider.name == 'cargoHoldThreshold':
            uicore.layer.shipui.sr.shipAlertContainer.AlertThresholdChanged('cargoHold')

    def CheckBoxChange(self, checkbox):
        notificationKey = checkbox.name[0:-len('NotificationEnabled')]
        if notificationKey in soundNotifications.keys():
            notification = SoundNotification(notificationKey)
            settings.user.notifications.Set(notification.activeFlagSettingsName, checkbox.checked)
            if checkbox.checked:
                sm.GetService('audio').SendUIEvent(notification.notificationEventName)
            uicore.layer.shipui.sr.shipAlertContainer.SetNotificationEnabled(notificationKey, checkbox.checked)
