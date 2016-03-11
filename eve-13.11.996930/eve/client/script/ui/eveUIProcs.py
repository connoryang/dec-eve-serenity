#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\eveUIProcs.py
import uthread
import eve.common.script.sys.eveCfg as util
import locks
import random
import svc
import carbonui.const as uiconst
import localization

class EveUIProcSvc(svc.uiProcSvc):
    __guid__ = 'svc.eveUIProcSvc'
    __replaceservice__ = 'uiProcSvc'
    __startupdependencies__ = ['cmd']

    def Run(self, *args):
        svc.uiProcSvc.Run(self, *args)
        self.uiCallbackDict = {None: self._NoneKeyIsInvalid_Callback,
         'OpenCharacterCustomization': self.__OpenCharacterCustomization_Callback,
         'CorpRecruitment': self._CorpRecruitment_Callback,
         'OpenCorporationPanel_Planets': self._OpenCorporationPanel_Planets_Callback,
         'OpenAuraInteraction': self.cmd.OpenAuraInteraction,
         'ExitStation': self.cmd.CmdExitStation,
         'OpenFitting': self.cmd.OpenFitting,
         'OpenShipHangar': self.cmd.OpenShipHangar,
         'OpenCargoBay': self.cmd.OpenCargoHoldOfActiveShip,
         'OpenDroneBay': self.cmd.OpenDroneBayOfActiveShip,
         'OpenMarket': self.cmd.OpenMarket,
         'OpenAgentFinder': self.cmd.OpenAgentFinder,
         'OpenStationDoor': self.__OpenStationDoor_Callback,
         'EnterHangar': self.cmd.CmdEnterHangar,
         'GiveNavigationFocus': self._GiveNavigationFocus_Callback}
        self.isOpeningPI = False

    def _PerformUICallback(self, callbackKey):
        callback = self.uiCallbackDict.get(callbackKey, None)
        if callback is not None:
            uthread.worker('_PerformUICallback_%s' % callbackKey, self._PerformUICallbackTasklet, callbackKey, callback)
            return True
        self.LogError('ActionObject.PerformUICallback: Unknown callbackKey', callbackKey)
        return False

    def _PerformUICallbackTasklet(self, callbackKey, callback):
        try:
            callback()
        except TypeError as e:
            self.LogError('ActionObject.PerformUICallback: callbackKey "%s" is associated with a non-callable object: %s' % (callbackKey, callback), e)

    def _NoneKeyIsInvalid_Callback(self):
        self.LogError('PerformUICallback called from ActionObject without the callbackKey property (it was None)!')

    def _CorpRecruitment_Callback(self):
        if util.IsNPC(session.corpid):
            self.cmd.OpenCorporationPanel_RecruitmentPane()
        else:
            self.cmd.OpenCorporationPanel()

    def _GiveNavigationFocus_Callback(self):
        sm.GetService('navigation').Focus()

    def _OpenCorporationPanel_Planets_Callback(self):
        if self.isOpeningPI:
            return
        self.isOpeningPI = True
        try:
            if sm.GetService('planetSvc').GetMyPlanets():
                self.cmd.OpenPlanets()
            else:
                systemData = sm.GetService('map').GetSolarsystemItems(session.solarsystemid2)
                systemPlanets = []
                for orbitalBody in systemData:
                    if orbitalBody.groupID == const.groupPlanet:
                        systemPlanets.append(orbitalBody)

                planetID = systemPlanets[random.randrange(0, len(systemPlanets))].itemID
                sm.GetService('viewState').ActivateView('planet', planetID=planetID)
                if not settings.user.suppress.Get('suppress.PI_Info', None):
                    uicore.Message('PlanetaryInteractionIntroText')
        finally:
            self.isOpeningPI = False

    def __OpenStationDoor_Callback(self):
        uicore.Message('CaptainsQuartersStationDoorClosed')

    def __OpenCharacterCustomization_Callback(self):
        if getattr(sm.GetService('map'), 'busy', False):
            return
        if uicore.Message('EnterCharacterCustomizationCQ', {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
            self.cmd.OpenCharacterCustomization()
