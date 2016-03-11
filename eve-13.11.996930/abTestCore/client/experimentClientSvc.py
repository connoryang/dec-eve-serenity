#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\abTestCore\client\experimentClientSvc.py
import service
import blue
from ..experimentClientMgr import ABTestClientManager

class ExperimentClientService(service.Service):
    __guid__ = 'svc.experimentClientSvc'
    service = 'svc.experimentClientSvc'
    __notifyevents__ = ['OnWindowOpened', 'OnWindowMaximized']

    def __init__(self):
        service.Service.__init__(self)
        self.manager = ABTestClientManager()

    def Run(self, memStream = None):
        pass

    def OnUserLogon(self, languageID):
        userLogonTime = blue.os.GetWallclockTime()

    def OnCharacterLogon(self):
        characterLogonTime = blue.os.GetWallclockTime()

    def LogAttemptToClickTutorialLink(self, tutorialID):
        self.LogFirstTimeActionTaken('tutorialLinkClick %s', str(tutorialID))

    def Initialize(self, languageID):
        characterLogonTime = blue.os.GetWallclockTime()
        self.manager.Initialize(languageID=languageID, logonTime=characterLogonTime, infoGatheringSvc=sm.GetService('infoGatheringSvc'))

    def TearDown(self):
        self.manager.TearDown()
        self.manager = ABTestClientManager()

    def IsTutorialEnabled(self):
        return self.manager.IsTutorialEnabled()

    def OpportunitiesEnabled(self):
        return self.manager.IsOpportunitiesEnabled()

    def ShouldStartInDungeon(self):
        return True

    def LogWindowOpenedActions(self, windowGuid):
        self.LogWindowOpenedCounter(windowGuid=windowGuid)
        self.LogFirstTimeActionTaken(action=windowGuid)

    def LogMapColorModeLoadedCounter(self, colorModeName):
        self.manager.LogMapColorModeLoadedCounter(colorModeName, session)

    def LogWindowOpenedCounter(self, windowGuid):
        self.manager.LogWindowOpenedCounter(windowGuid, session)

    def LogFirstTimeActionTaken(self, action):
        now = blue.os.GetWallclockTime()
        self.manager.LogFirstTimeActionTaken(action, session, now)

    def OnWindowOpened(self, wnd):
        self.LogWindowOpenedActions(wnd.__class__.__name__)

    def OnWindowMaximized(self, wnd, wasMinimized):
        if not wasMinimized:
            return
        self.LogWindowOpenedActions(wnd.__class__.__name__)
