#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\autoMoveBot.py
from service import Service, ROLE_GMH
import blue
import types
import chat
import uthread
import locks
import uiutil
import carbonui.const as uiconst
import const
import uiprimitives
import uicontrols

class AutoMoveBot(Service):
    __guid__ = 'svc.automovebot'
    __notifyevents__ = ['OnChannelsJoined', 'OnLSC']
    CHANNEL_NAME = 'moveme'
    MOVE_PHRASE = 'moveme'
    DESTINATION_ID = 30003280

    def __init__(self):
        Service.__init__(self)
        self.lscService = sm.GetService('LSC')
        self.slashRemote = sm.RemoteSvc('slash')
        self.channelID = None
        self.waitingList = []
        self.moveRunning = False
        self.channelName = self.CHANNEL_NAME
        self.movePhrase = self.MOVE_PHRASE
        self.destinationID = self.DESTINATION_ID

    def Stop(self, memStream = None):
        self.StopBot()

    def StartBot(self):
        self.waitingList = []
        sm.ScatterEvent('OnAutoMoveBotQueueChange', 0)
        uthread.new(self.PrepareMoveChannel)
        self.moveRunning = True
        uthread.new(self.MoveCharacterThread)
        sm.ScatterEvent('OnAutoMoveBotStateChanged', 'start')

    def StopBot(self):
        self.moveRunning = False
        self.lscService.LeaveChannel(self.GetChannelIDFromName(self.channelName), unsubscribe=1)
        sm.ScatterEvent('OnAutoMoveBotStateChanged', 'stop')

    def GetChannelIDFromName(self, name):
        for channel in self.lscService.GetChannels():
            if type(channel) == blue.DBRow:
                if channel[4] == name.lower():
                    return channel[0]

    @staticmethod
    def GetCharacterIDFromLSC(fullID):
        if type(fullID) == types.IntType:
            return fullID
        return fullID[2][0]

    def PrepareMoveChannel(self):
        channelID = self.GetChannelIDFromName(self.channelName)
        if channelID:
            self.lscService.JoinChannel(channelID)
            self.channelID = channelID
        else:
            self.lscService.CreateOrJoinChannel(self.channelName)

    def OnChannelsJoined(self, channelIDs):
        if type(channelIDs) != types.ListType:
            return
        for channelID in channelIDs:
            channelInfo = self.lscService.GetChannelInfo(channelID).Get('info')
            if channelInfo is None:
                continue
            name = channelInfo[2]
            if self.channelName.lower() == name:
                self.channelID = channelID
                break

    def OnLSC(self, channelID, estimatedMembercount, method, who, *args):
        if self.channelID is None:
            return
        if channelID != self.channelID:
            return
        charID = self.GetCharacterIDFromLSC(who)
        if charID == session.charid or charID in self.waitingList:
            return
        if method == 'SendMessage':
            if len(args[0]) == 0:
                return
            message = args[0][0]
            if message.lower() == self.movePhrase.lower():
                with locks.TempLock('waitingList', locks.RLock):
                    self.waitingList.insert(0, charID)
                    sm.ScatterEvent('OnAutoMoveBotQueueChange', len(self.waitingList))

    def MoveCharacterThread(self):
        while self.moveRunning is True:
            if len(self.waitingList) > 0:
                charID = None
                with locks.TempLock('waitingList', locks.RLock):
                    charID = self.waitingList.pop()
                    sm.ScatterEvent('OnAutoMoveBotQueueChange', len(self.waitingList))
                self.MoveCharacter(charID)
            else:
                blue.pyos.synchro.SleepWallclock(2000)

    def MoveCharacter(self, charID):
        retriesLeft = 10
        while retriesLeft > 0:
            try:
                self.slashRemote.SlashCmd('/tr %s %s' % (charID, self.destinationID))
                self.lscService.AccessControl(self.channelID, charID, chat.CHTMODE_DISALLOWED, None, None)
                self.lscService.AccessControl(self.channelID, charID, chat.CHTMODE_NOTSPECIFIED, None, None)
                break
            except (UserError, RuntimeError):
                retriesLeft -= 1
                blue.pyos.synchro.SleepSim(2000)


class AutoMoveBotWnd(uicontrols.Window):
    __guid__ = 'form.autoMoveBot'
    __neocommenuitem__ = (('AutoMoveBot', 'autoMoveBot'), True, ROLE_GMH)
    __notifyevents__ = ['OnAutoMoveBotQueueChange', 'OnAutoMoveBotStateChanged']

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.SetMinSize([320, 150])
        self.SetWndIcon(None)
        self.SetCaption('AutoMoveBot Control')
        self.MakeUnResizeable()
        self.SetTopparentHeight(0)
        self.Begin()

    def Begin(self):
        autoMoveBotSvc = sm.GetService('automovebot')
        main = uiprimitives.Container(name='main', parent=self.sr.main, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.GenerateInputLine(main, 'channelInput', 'Channel name:', autoMoveBotSvc.CHANNEL_NAME).Disable()
        self.GenerateInputLine(main, 'phraseInput', 'Trigger-phrase:', autoMoveBotSvc.MOVE_PHRASE).Disable()
        self.GenerateInputLine(main, 'destInput', 'Destination ID:', autoMoveBotSvc.DESTINATION_ID).Disable()
        queueContainer = uiprimitives.Container(parent=main, align=uiconst.TOALL, height=16, top=const.defaultPadding)
        self.queueLabel = uicontrols.Label(text='Queue Size:', name='txtQueue', parent=queueContainer, align=uiconst.TOALL, height=12, top=10, left=25, letterspace=1, linespace=9, uppercase=1, state=uiconst.UI_NORMAL)
        buttons = [['Start',
          self.StartBot,
          None,
          81], ['Stop',
          self.StopBot,
          None,
          81], ['Close',
          self.Hide,
          None,
          81]]
        self.btns = uicontrols.ButtonGroup(btns=buttons, line=1, parent=main)
        self.SetRunning(False)

    @staticmethod
    def GenerateInputLine(parent, name, title, defaultValue):
        container = uiprimitives.Container(parent=parent, align=uiconst.TOTOP, height=16, top=const.defaultPadding)
        container.padLeft = 5
        container.padRight = 5
        label = uicontrols.Label(text=title, name='txt%s' % name, parent=container, align=uiconst.TOLEFT, height=12, top=5, left=8, fontsize=10, letterspace=1, linespace=9, uppercase=1, state=uiconst.UI_NORMAL)
        label.rectTop = -2
        inputField = uicontrols.SinglelineEdit(name=name, parent=container, setvalue=str(defaultValue), left=5, width=200, height=20, align=uiconst.TORIGHT)
        return inputField

    def Hide(self, *args):
        self.Close()

    def StartBot(self, *args):
        autoMoveBotSvc = sm.GetService('automovebot')
        autoMoveBotSvc.StartBot()
        main = uiutil.GetChild(self.sr.main, 'main')
        autoMoveBotSvc.channelName = uiutil.GetChild(main, 'channelInput').GetValue()
        autoMoveBotSvc.movePhrase = uiutil.GetChild(main, 'phraseInput').GetValue()
        autoMoveBotSvc.destinationID = uiutil.GetChild(main, 'destInput').GetValue()
        self.SetRunning(True)

    def StopBot(self, *args):
        sm.GetService('automovebot').StopBot()
        self.SetRunning(False)

    def SetRunning(self, state):
        main = uiutil.GetChild(self.sr.main, 'main')
        channelInput = uiutil.GetChild(main, 'channelInput')
        phraseInput = uiutil.GetChild(main, 'phraseInput')
        destInput = uiutil.GetChild(main, 'destInput')
        startBtn = uiutil.GetChild(self.btns, 'Start_Btn')
        stopBtn = uiutil.GetChild(self.btns, 'Stop_Btn')
        if state is True:
            startBtn.Disable()
            stopBtn.Enable()
            channelInput.Disable()
            phraseInput.Disable()
            destInput.Disable()
        else:
            startBtn.Enable()
            stopBtn.Disable()
            channelInput.Enable()
            phraseInput.Enable()
            destInput.Enable()

    def OnAutoMoveBotQueueChange(self, size):
        self.queueLabel.SetText('Queue Size: %s' % str(size))

    def OnAutoMoveBotStateChanged(self, state):
        if state == 'start':
            self.SetRunning(True)
        elif state == 'stop':
            self.SetRunning(False)
