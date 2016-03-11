#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\extras\tourneyBanUI.py
import evetypes
import service
import uiprimitives
import uicontrols
import carbonui.const as uiconst
import blue
import base
import const

class TourneyBanUISvc(service.Service):
    __guid__ = 'svc.tourneyBanUI'
    __notifyevents__ = ['OnTournamentPerformBan']

    def OnTournamentPerformBan(self, banID, numBans, curBans, deadline, respondToNodeID, tourneyID):
        self.LogInfo('OnTourneyBan recv', banID, numBans, curBans, deadline, respondToNodeID)
        TourneyBanUI.CloseIfOpen()
        tourneyMgr = sm.RemoteSvc('tourneyMgr')
        tournamentShipDetails = tourneyMgr.QueryShipList(tourneyID)
        shipList = tournamentShipDetails['allowedShipList']
        banBox = TourneyBanUI.Open()
        banBox.Execute(banID, numBans, curBans, deadline, respondToNodeID, shipList)
        banBox.ShowModal()


class TourneyBanUI(uicontrols.Window):
    __guid__ = 'form.TourneyBanUI'
    default_alwaysLoadDefaults = True

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.SetCaption('Tournament Ban Prompt')
        self.SetMinSize((300, 375))
        self.SetTopparentHeight(0)

    def SetModalResult(self, result, caller = None):
        if result == uiconst.ID_OK:
            return
        super(TourneyBanUI, self).SetModalResult(result, caller)

    def Execute(self, banID, numBans, curBans, deadline, respondToNodeID, shipList):
        self.banID = banID
        self.deadline = deadline
        self.respondToNodeID = respondToNodeID
        self.resetButton = uicontrols.Button(label='Submit Ban' if numBans > 0 else 'Okay', parent=self.sr.main, align=uiconst.TOBOTTOM, func=self.Submit, state=uiconst.UI_NORMAL, padding=5)
        uicontrols.EveLabelLarge(text="Let's ban some ships!" if numBans > 0 else "Here's the bans:", parent=self.sr.main, align=uiconst.TOTOP, top=10, padding=5, color=(0.5, 0.5, 1, 1))
        uicontrols.Label(text='You have banned:', parent=self.sr.main, align=uiconst.TOTOP, top=5, padding=5)
        uicontrols.Label(text='<br>'.join([ evetypes.GetName(typeID) for typeID in curBans[0] ]), padding=5, parent=self.sr.main, align=uiconst.TOTOP)
        uicontrols.Label(text='They have banned:', parent=self.sr.main, align=uiconst.TOTOP, top=5, padding=5)
        uicontrols.Label(text='<br>'.join([ evetypes.GetName(typeID) for typeID in curBans[1] ]), padding=5, parent=self.sr.main, align=uiconst.TOTOP)
        ships = []
        for typeID in evetypes.GetTypeIDsByCategory(const.categoryShip):
            if typeID in [ tup[1] for tup in shipList ]:
                if evetypes.IsPublished(typeID):
                    name = evetypes.GetName(typeID)
                    if not name.startswith('[no messageID:'):
                        ships.append((name, typeID))

        banOptions = [('Pass', -1)] + sorted(ships)
        self.banChoices = []
        for banNum in xrange(numBans):
            self.banChoices.append(uicontrols.Combo(label='Ban: ', parent=self.sr.main, options=banOptions, top=20, padding=5, align=uiconst.TOTOP))

        if numBans > 0:
            banCont = uiprimitives.Container(name='banTimer', parent=self.sr.main, align=uiconst.TOTOP, height=50)
            self.countdownText = uicontrols.Label(parent=banCont, align=uiconst.CENTER, fontsize=36, color=(1, 0, 0, 1))
            self.countdownTimer = base.AutoTimer(100, self.UpdateTimer)
        uicore.registry.SetFocus(self)
        self.MakeUnKillable()

    def Submit(self, *args):
        machoNet = sm.GetService('machoNet')
        remoteTourneyMgr = machoNet.ConnectToRemoteService('tourneyMgr', self.respondToNodeID)
        banTypes = []
        for choice in self.banChoices:
            shipTypeToBan = choice.GetValue()
            if shipTypeToBan != -1:
                banTypes.append(shipTypeToBan)

        remoteTourneyMgr.BanShip(self.banID, banTypes)
        self.Close()

    def UpdateTimer(self):
        timeDiffMS = max(0, blue.os.TimeDiffInMs(blue.os.GetWallclockTime(), self.deadline))
        self.countdownText.text = '%.1f' % (float(timeDiffMS) / 1000.0,)
        if timeDiffMS == 0:
            self.MakeKillable()
            self.countdownTimer = None
