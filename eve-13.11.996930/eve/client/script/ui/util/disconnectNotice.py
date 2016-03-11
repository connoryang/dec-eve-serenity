#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\util\disconnectNotice.py
from carbon.client.script.sys import appUtils
from carbon.common.script.net.ExceptionMappingGPCS import TRANSPORT_CLOSED_MESSAGES
import carbonui.primitives as uiprimitives
import localization
import carbonui.const as uiconst
import bluepy
from eve.client.script.ui.shared.messagebox import MessageBox

class NoLog(object):

    def LogInfo(self):
        pass

    def LogError(self):
        pass


class DisconnectNotice(object):

    def __init__(self, logProvider):
        if logProvider is None:
            logProvider = NoLog()
        self.logProvider = logProvider

    def OnDisconnect(self, reason = 0, msg = ''):
        if msg in TRANSPORT_CLOSED_MESSAGES:
            msg = localization.GetByLabel(TRANSPORT_CLOSED_MESSAGES[msg])
        self.logProvider.LogInfo('Received OnDisconnect with reason=', reason, ' and msg=', msg)
        if reason in (0, 1):
            self.logProvider.LogError('GameUI::OnDisconnect', reason, msg)
            audio = sm.GetService('audio')
            audio.Deactivate()
            self.ShowDisconnectNotice(notice=msg)

    def ShowDisconnectNotice(self, notice = None):
        notice = notice or localization.GetByLabel('UI/Shared/GenericConnectionLost')
        msgbox = MessageBox.Open(windowID='DisconnectNotice', parent=uicore.desktop, idx=0)
        msgbox.MakeUnResizeable()
        msgbox.MakeUnpinable()
        msgbox.MakeUnKillable()
        canReboot = appUtils.CanReboot()
        okLabel = localization.GetByLabel('UI/Commands/CmdRestart') if canReboot else localization.GetByLabel('UI/Commands/CmdQuit')
        buttons = uiconst.OKCANCEL if canReboot else uiconst.OK
        cancelLabel = localization.GetByLabel('UI/Commands/CmdQuit') if canReboot else None
        msgbox.Execute(notice, localization.GetByLabel('UI/Shared/ConnectionLost'), buttons, uiconst.INFO, None, okLabel=okLabel, cancelLabel=cancelLabel)
        uicore.layer.hint.display = False
        blackOut = uiprimitives.fill.Fill(parent=uicore.layer.modal, color=(0, 0, 0, 0), idx=1)
        uicore.animations.MorphScalar(blackOut, 'opacity', startVal=0, endVal=0.75, duration=1.0)
        modalResult = msgbox.ShowModal()
        if canReboot and modalResult == uiconst.ID_OK:
            appUtils.Reboot('connection lost')
        else:
            bluepy.Terminate('User requesting close after client disconnect')
