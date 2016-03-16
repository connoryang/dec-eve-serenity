#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\behaviortools\clientdebugadaptors.py
import logging
import eve.common.script.net.eveMoniker as moniker
from eve.devtools.script.behaviortools.debugwindow import BehaviorDebugWindow
import uthread2
import signals
logger = logging.getLogger(__name__)
EVENT_BEHAVIOR_DEBUG_UPDATE = 'OnBehaviorDebugUpdate'
EVENT_BEHAVIOR_DEBUG_CONNECT_REQUEST = 'OnBehaviorDebugConnectRequest'
EVENT_BEHAVIOR_DEBUG_DISCONNECT_REQUEST = 'OnBehaviorDebugDisconnectRequest'

class UpdateListener(object):

    def __init__(self):
        self.messenger = signals.Messenger()
        self.behaviorDebuggersByEntryKey = {}
        sm.RegisterForNotifyEvent(self, EVENT_BEHAVIOR_DEBUG_UPDATE)
        sm.RegisterForNotifyEvent(self, EVENT_BEHAVIOR_DEBUG_CONNECT_REQUEST)
        sm.RegisterForNotifyEvent(self, EVENT_BEHAVIOR_DEBUG_DISCONNECT_REQUEST)

    def AddObserverForItemId(self, entryKey, handler):
        self.messenger.UnsubscribeAllFromMessage(entryKey)
        self.messenger.SubscribeToMessage(entryKey, handler)

    def RemoveObserverForItemId(self, entryKey, handler):
        try:
            self.messenger.UnsubscribeFromMessage(entryKey, handler)
        except:
            logger.error('Failed to remove observer entryKey=%s handler=%s', entryKey, handler)

    def OnBehaviorDebugUpdate(self, entryKey, *args, **kwargs):
        self.messenger.SendMessage(entryKey, *args, **kwargs)

    def TryConnectDebugger(self, entryKey):
        try:
            debugger = ClientBehaviorDebugger(entryKey)
            debugger.Connect()
            self.behaviorDebuggersByEntryKey[entryKey] = debugger
        except:
            logger.exception('failed to connect to debugger for entryKey=%s', entryKey)

    def OnBehaviorDebugConnectRequest(self, itemIDs):
        itemIDs = sorted(itemIDs)
        for entryKey in itemIDs:
            self.TryConnectDebugger(entryKey)

    def TryDisconnectDebugger(self, entryKey):
        try:
            debugger = self.behaviorDebuggersByEntryKey.pop(entryKey)
            debugger.Disconnect()
        except:
            logger.exception('failed to disconnect to debugger for entryKey=%s', entryKey)

    def OnBehaviorDebugDisconnectRequest(self, itemIDs):
        for entryKey in itemIDs:
            self.TryDisconnectDebugger(entryKey)

    def HasDebugger(self, entryKey):
        return entryKey in self.behaviorDebuggersByEntryKey


updateListener = UpdateListener()

class ClientBehaviorDebugger(object):

    def __init__(self, entryKey):
        self.entryKey = entryKey
        self.tree = []
        self.treeMap = {}
        self.events = []
        self.debugWindow = None
        self.isConnected = False

    def Connect(self):
        logger.debug('Debugger connecting to behavior of entity %s', self.entryKey)
        updateListener.AddObserverForItemId(self.entryKey, self.OnBehaviorDebugUpdate)
        entityLocation = moniker.GetEntityLocation()
        treeData = entityLocation.EnableBehaviorDebugging(self.entryKey)
        self.isConnected = True
        uthread2.StartTasklet(self.SetupDebugTree, treeData)

    def Disconnect(self):
        logger.debug('Debugger disconnecting from behavior of entity %s', self.entryKey)
        try:
            updateListener.RemoveObserverForItemId(self.entryKey, self.OnBehaviorDebugUpdate)
            entityLocation = moniker.GetEntityLocation()
            entityLocation.DisableBehaviorDebugging(self.entryKey)
            self.isConnected = False
            if self.debugWindow is not None:
                self.debugWindow.Close()
            sm.UnregisterForNotifyEvent(self, 'OnSessionChanged')
        except:
            logger.exception('Failed while disconnecting :(')

    def OnBehaviorDebugUpdate(self, events, taskStatuses, tasksSeen, blackboards, *args, **kwargs):
        if self.debugWindow is None:
            return
        self.debugWindow.LoadEvents(events)
        self.debugWindow.UpdateStatuses(taskStatuses)
        self.debugWindow.UpdateTasksSeen(tasksSeen)
        self.debugWindow.LoadBlackboard(blackboards)

    def SetupDebugTree(self, treeData):
        self.debugWindow = BehaviorDebugWindow.Open(windowID='BehaviorDebugWindow_' + str(self.entryKey))
        self.debugWindow.SetController(self)
        self.debugWindow.LoadBehaviorTree(treeData)
        sm.RegisterForNotifyEvent(self, 'OnSessionChanged')

    def IsConnected(self):
        return self.isConnected

    def OnSessionChanged(self, isRemote, sess, change):
        if 'solarsystemid2' in change:
            if self.debugWindow is not None:
                self.debugWindow.Close()
