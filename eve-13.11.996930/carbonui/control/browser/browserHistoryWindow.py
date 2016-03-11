#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\control\browser\browserHistoryWindow.py
import carbonui.const as uiconst
import localization
from carbonui.control.window import WindowCoreOverride as Window
from carbonui.control.buttons import ButtonCoreOverride as Button
from carbonui.control.scroll import ScrollCoreOverride as Scroll
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore

class BrowserHistoryWindowCore(Window):
    __guid__ = 'uicls.BrowserHistoryWindowCore'
    default_windowID = 'BrowserHistoryWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/Browser/BrowserHistory/BrowserHistoryCaption'))
        self.SetMinSize((400, 256))
        mainArea = self.GetMainArea()
        mainArea.clipChildren = 0
        mainArea.padding = 6
        clearHistory = Button(parent=mainArea, label=localization.GetByLabel('UI/Browser/BrowserHistory/ClearHistory'), func=self.ClearHistory, align=uiconst.BOTTOMRIGHT)
        self.scroll = Scroll(parent=mainArea, padBottom=clearHistory.height + 6)
        self.scroll.sr.maxDefaultColumns = {localization.GetByLabel('UI/Browser/BrowserHistory/URL'): 250,
         localization.GetByLabel('UI/Browser/BrowserHistory/Title'): 250}
        self.LoadHistory()

    def LoadHistory(self):
        self.selected = None
        scrolllist = []
        for each in sm.GetService('urlhistory').GetHistory():
            if each is not None:
                try:
                    label = localization.GetByLabel('UI/Browser/BrowserHistory/Row', title=each.title, url=each.url, date=each.ts)
                    scrolllist.append(ScrollEntryNode(decoClass=SE_GenericCore, label=label, retval=each, OnClick=self.OnEntryClick, OnDblClick=self.OnEntryDblClick))
                except:
                    continue

        self.scroll.sr.id = 'history_window_scroll_id'
        self.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Browser/BrowserHistory/Title'), localization.GetByLabel('UI/Browser/BrowserHistory/URL'), localization.GetByLabel('UI/Browser/BrowserHistory/Date')])

    def OnEntryClick(self, node):
        self.selectedEntry = node.sr.node.retval

    def OnEntryDblClick(self, node):
        self.OnEntryClick(node)
        if uicore.commandHandler:
            uicore.commandHandler.OpenBrowser(url=str(self.selectedEntry.url))

    def ClearHistory(self, *args):
        sm.GetService('urlhistory').ClearAllHistory()
        self.LoadHistory()
        sm.ScatterEvent('OnBrowserHistoryCleared')


class BrowserHistoryWindowCoreOverride(BrowserHistoryWindowCore):
    pass
