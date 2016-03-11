#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\windowManager.py
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.inflight.activeitem import ActiveItem
from eve.client.script.ui.inflight.drone import DroneView
from eve.client.script.ui.inflight.overview import OverView
from eve.client.script.ui.shared.maps.browserwindow import MapBrowserWnd
from eve.client.script.ui.station.lobby import Lobby
import carbonui.const as uiconst

class WindowManager(Window):
    __guid__ = 'form.WindowManager'
    default_windowID = 'WindowManager'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetWndIcon(None)
        self.SetCaption('Window manager')
        self.SetTopparentHeight(10)
        self.SetMinSize([360, 220])
        options = []
        for wndCls in Window.__subclasses__():
            options.append((wndCls.__name__, wndCls))

        options.sort()
        topCont = Container(name='params', parent=self.sr.main, align=uiconst.TOTOP, pad=(5, 5, 5, 5), pos=(0, 10, 0, 30))
        self.mainCont = Container(name='params', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 50), padding=(5, 15, 5, 5))
        self.extrasCont = Container(name='params', parent=self.sr.main, align=uiconst.TOALL, padding=(5, 15, 5, 5))
        self.combo = Combo(parent=topCont, label='Select window', options=options, name='', select=settings.user.ui.Get('windowManagerOpenWindow'), callback=self.OnComboChanged, pos=(5, 0, 0, 0), width=150, align=uiconst.TOPLEFT)
        self.startupArgs = SinglelineEdit(name='', label='attributes', parent=topCont, setvalue='', align=uiconst.TOPLEFT, left=165, width=100)
        Button(parent=topCont, label='Load', align=uiconst.RELATIVE, func=self.OpenWindow, pos=(300, 0, 0, 0))
        self.filenameEdit = SinglelineEdit(name='', label='Location', parent=self.mainCont, setvalue='', align=uiconst.TOTOP, top=15, readonly=True)
        Label(text='RELOAD', parent=self.extrasCont, top=10, state=uiconst.UI_NORMAL)
        Line(parent=self.extrasCont, align=uiconst.TOTOP)
        buttonCont = Container(name='buttonCont', parent=self.extrasCont, align=uiconst.TOTOP, pos=(0, 30, 0, 30))
        Button(parent=buttonCont, label='ShipUI', align=uiconst.TOLEFT, func=self.ReloadShipUI)
        Button(parent=buttonCont, label='NEOCOM', align=uiconst.TOLEFT, func=self.ReloadNeocom, padLeft=1)
        Button(parent=buttonCont, label='Info Panels', align=uiconst.TOLEFT, func=self.ReloadInfoPanels, padLeft=1)
        Button(parent=buttonCont, label='Lobby', align=uiconst.TOLEFT, func=self.ReloadLobby, padLeft=1)
        Button(parent=buttonCont, label='Overview', align=uiconst.TOLEFT, func=self.ReloadOverview, padLeft=1)
        Button(parent=buttonCont, label='Mapbrowser', align=uiconst.TOLEFT, func=self.ReloadMapBrowser, padLeft=1)
        self.UpdateInfo(self.combo.GetKey(), self.combo.GetValue())

    def OnComboChanged(self, combo, key, wndCls):
        self.UpdateInfo(key, wndCls)

    def UpdateInfo(self, key, wndCls):
        self.filenameEdit.SetValue(wndCls.ApplyAttributes.func_code.co_filename)
        settings.user.ui.Set('windowManagerOpenWindow', wndCls)

    def OpenWindow(self, *args):
        windowClass = self.combo.GetValue()
        windowClass.CloseIfOpen()
        attributes = {}
        try:
            attributesStr = self.startupArgs.GetValue()
            if attributesStr:
                for s in attributesStr.split(','):
                    keyword, value = s.split('=')
                    keyword = keyword.strip()
                    value = value.strip()
                    try:
                        if value.find('.') != -1:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass

                    if value == 'None':
                        value = None
                    attributes[keyword] = value

        except:
            eve.Message('CustomInfo', {'info': 'attributes must be on the form: attr1=1, attr2=Some random text'})
            raise

        windowClass.Open(**attributes)

    def ReloadShipUI(self, *args):
        if eve.session.stationid is None:
            uicore.layer.shipui.CloseView()
            uicore.layer.shipui.OpenView()

    def ReloadNeocom(self, *args):
        sm.GetService('neocom').Reload()

    def ReloadInfoPanels(self, *args):
        sm.GetService('infoPanel').Reload()

    def ReloadLobby(self, *args):
        if session.stationid:
            Lobby.CloseIfOpen()
            Lobby.Open()

    def ReloadMapBrowser(self, *args):
        MapBrowserWnd.CloseIfOpen()
        uicore.cmd.OpenMapBrowser()

    def ReloadOverview(self, *args):
        OverView.CloseIfOpen()
        if session.solarsystemid:
            sm.GetService('tactical').InitOverview()
        ActiveItem.CloseIfOpen()
        if session.solarsystemid:
            sm.GetService('tactical').InitSelectedItem()
        DroneView.CloseIfOpen()
        if session.solarsystemid:
            sm.GetService('tactical').InitDrones()
