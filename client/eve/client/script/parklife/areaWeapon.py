#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\areaWeapon.py
from appConst import defaultPadding
from carbon.common.script.sys.service import Service
import geo2
import uiprimitives
import uicontrols
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui.const import TOPLEFT
import decometaclass
import trinity
import uthread2
from utillib import KeyVal

class WeaponTargetBall(decometaclass.WrapBlueClass('destiny.ClientBall')):

    def __init__(self):
        self.model = trinity.EveRootTransform()


class AreaWeaponToolsWindow(uicontrols.Window):
    default_windowID = 'areaweapontools'


class AreaWeaponSvc(Service):
    __dependencies__ = ['michelle', 'sceneManager']
    __guid__ = 'svc.areaWeapon'
    __servicename__ = 'areaWeapon'
    __displayname__ = 'Area weapon service'
    __neocommenuitem__ = (('Area weapon [prototype]', None), 'ShowWindow', ROLE_GML)
    targetStartOffset = None
    targetEndOffset = None

    def Run(self, memStream = None):
        self.LogInfo('Starting AreaWeapon Service')

    def SetTargetingOffsets(self, startOffset, endOffset):
        self.targetStartOffset = startOffset
        self.targetEndOffset = endOffset
        self.startPosBox.SetText('%d, %d, %d' % (startOffset[0], startOffset[1], startOffset[2]))
        self.endPosBox.SetText('%d, %d, %d' % (endOffset[0], endOffset[1], endOffset[2]))

    def FireOnServer(self, moduleID):
        sm.RemoteSvc('superWeaponMgr').ActivateSlashModule(moduleID, self.targetStartOffset, self.targetEndOffset)

    def _PlayLocalFireEffect(self, sourceID, duration = 20):
        ballpark = self.michelle.GetBallpark()
        graphicInfo = KeyVal(startTargetOffset=self.targetStartOffset, endTargetOffset=self.targetEndOffset, warmupDuration=10000, damageDuration=10000)
        ballpark.OnSpecialFX(sourceID, None, None, None, None, 'effects.SlashStretch', 0, 1, 0, duration * 1000, graphicInfo=graphicInfo)

    def ShowWindow(self):
        wnd = AreaWeaponToolsWindow.GetIfOpen()
        if wnd:
            wnd.Maximize()
            return
        wnd = AreaWeaponToolsWindow.Open()
        wnd.SetWndIcon('41_13')
        wnd.SetTopparentHeight(0)
        wnd.SetCaption('Area-weapon prototype')
        wnd.SetMinSize([250, 300])
        wnd.MakeUnResizeable()
        self.width = 250
        self.height = 200
        mainCont = uiprimitives.Container(name='mainCont', parent=wnd.sr.main, pos=(defaultPadding,
         defaultPadding,
         defaultPadding,
         defaultPadding))
        uicontrols.Label(text='Start x,y,x', parent=mainCont, pos=(10, 5, 0, 0), align=TOPLEFT)
        self.startPosBox = uicontrols.SinglelineEdit(name='startPos', parent=mainCont, pos=(100, 5, 140, 20), align=TOPLEFT)
        uicontrols.Label(text='End x,y,z', parent=mainCont, pos=(10, 25, 0, 0), align=TOPLEFT)
        self.endPosBox = uicontrols.SinglelineEdit(name='endPos', parent=mainCont, pos=(100, 25, 140, 20), align=TOPLEFT)
        uicontrols.Label(text='Max angle', parent=mainCont, pos=(10, 55, 0, 0), align=TOPLEFT)
        self.angleBox = uicontrols.SinglelineEdit(name='angle', parent=mainCont, pos=(100, 55, 140, 20), align=TOPLEFT)
        uicontrols.Label(text='Duration (s)', parent=mainCont, pos=(10, 85, 0, 0), align=TOPLEFT)
        self.durationBox = uicontrols.SinglelineEdit(name='duration', parent=mainCont, ints=(1, 30), pos=(100, 85, 140, 20), align=TOPLEFT)
        uicontrols.Label(text='Beam length', parent=mainCont, pos=(10, 110, 0, 0), align=TOPLEFT)
        self.beamLengthBox = uicontrols.SinglelineEdit(name='beamLength', parent=mainCont, pos=(100, 110, 140, 20), align=TOPLEFT)
        self.localFireBtn = uicontrols.Button(parent=mainCont, name='LocalFire', label='LOCAL FIRE!', pos=(80, 250, 0, 0), func=self.OnLocalFireButton, align=TOPLEFT)
        self.resetBtn = uicontrols.Button(parent=mainCont, name='Reset', label='Reset', pos=(170, 250, 0, 0), func=self.OnResetButton, align=TOPLEFT)
        self._ResetParameters()

    def _ResetParameters(self):
        self.durationBox.SetText('20')
        self.beamLengthBox.SetText('100000')
        self.angleBox.SetText('40')
        self.SetTargetingOffsets((-80000, 5000, 60000), (-80000, -5000, -60000))

    def OnResetButton(self, *args):
        self._ResetParameters()

    def OnLocalFireButton(self, *args):
        self._OnLocalFireButton(*args)

    def _OnLocalFireButton(self, *args):
        startOffset = geo2.VectorD([ float(v.strip()) for v in self.startPosBox.text.strip().split(',') ])
        endOffset = geo2.VectorD([ float(v.strip()) for v in self.endPosBox.text.strip().split(',') ])
        self.SetTargetingOffsets(startOffset, endOffset)
        duration = float(self.durationBox.text.strip())
        self._PlayLocalFireEffect(session.shipid, duration=duration)

    def GetDuration(self):
        try:
            return float(self.durationBox.text.strip())
        except AttributeError:
            return 20.0

    def GetAngle(self):
        try:
            return float(self.angleBox.text.strip())
        except AttributeError:
            return 30.0

    def GetBeamLength(self):
        try:
            return float(self.beamLengthBox.text.strip())
        except AttributeError:
            return 100000.0
