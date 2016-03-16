#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\networkdatamonitor.py
import operator
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveWindow import Window
import log
import uthread2
import util
PROPS = [('Packets out', 'packets_out', 0),
 ('Packets in', 'packets_in', 0),
 ('Kilobytes out', 'bytes_out', 1),
 ('Kilobytes in', 'bytes_in', 1)]

class NetworkDataMonitor(Window):
    default_caption = 'Network Data Monitor'
    default_windowID = 'networkdatamonitor'
    default_minSize = (400, 300)
    refreshDelay = 0.5

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.Reset()
        self.SetTopparentHeight(4)
        self.settingsContainer = Container(parent=self.sr.main, align=uiconst.TOBOTTOM, height=16, padding=8)
        Button(parent=self.settingsContainer, label='Reset', align=uiconst.CENTER, func=self.Reset)
        container = Container(parent=self.sr.main, align=uiconst.TOALL, padding=8)
        statusHeader = ' '
        for tme in self.intvals:
            statusHeader += '<t><right>%s' % util.FmtDate(long(tme * 10000), 'ss')

        statusHeader += '<t><right>total'
        self.statusLabels = []
        txt = Label(parent=container, align=uiconst.TOPLEFT, text=statusHeader, tabs=[80,
         130,
         180,
         230,
         280,
         330,
         380], state=uiconst.UI_DISABLED)
        for i in xrange(7):
            statusLabel = Label(parent=container, text='', top=(i + 1) * txt.height + 1, align=uiconst.TOPLEFT, tabs=[80,
             130,
             180,
             230,
             280,
             330,
             380], state=uiconst.UI_DISABLED)
            self.statusLabels.append(statusLabel)

        self.PopulateLabels()
        uthread2.StartTasklet(self.Refresh)

    def Reset(self, *args):
        self.intvals = [5000,
         10000,
         15000,
         30000,
         60000]
        self.counter = [[],
         [],
         [],
         [],
         [],
         []]
        self.ticker = 0
        self.packets_outTotal = 0
        self.packets_inTotal = 0
        self.bytes_outTotal = 0
        self.bytes_inTotal = 0
        self.laststats = {}
        self.lastresetstats = sm.GetService('machoNet').GetConnectionProperties()

    def Refresh(self):
        while not self.destroyed:
            uthread2.Sleep(self.refreshDelay)
            self.PopulateLabels()

    def PopulateLabels(self, *args):
        self.ticker += self.intvals[0]
        if self.ticker > self.intvals[-1]:
            self.ticker = self.intvals[0]
        stats = sm.GetService('machoNet').GetConnectionProperties()
        if self.laststats == {}:
            self.laststats = stats
        if self.lastresetstats != {}:
            for key in stats.iterkeys():
                stats[key] = stats[key] - self.lastresetstats[key]

        for i in xrange(len(self.counter) - 1):
            self.counter[i].append([ stats[key] - self.laststats[key] for header, key, K in PROPS ])
            self.counter[i] = self.counter[i][-(self.intvals[i] / 1000):]

        self.counter[-1].append([ stats[key] - self.laststats[key] for header, key, K in PROPS ])
        if not self.display:
            self.laststats = stats
            return
        valueIdx = 0
        for header, key, K in PROPS:
            statusstr = '%s' % header
            for intvals in self.counter:
                value = reduce(operator.add, [ intval[valueIdx] for intval in intvals ], 0)
                if not value:
                    statusstr += '<t><right>-'
                else:
                    statusstr += '<t><right>%s' % [value, '%.1f' % (value / 1024.0)][K]

            self.statusLabels[valueIdx].text = statusstr
            valueIdx += 1

        self.statusLabels[valueIdx].text = 'Outstanding<t><right>%s' % stats['calls_outstanding']
        valueIdx += 1
        self.statusLabels[valueIdx].text = 'Blocking Calls<t><right>%s' % stats['blocking_calls']
        valueIdx += 1
        block_time = stats['blocking_call_times']
        if block_time >= 0:
            secs = util.SecsFromBlueTimeDelta(block_time)
            self.statusLabels[valueIdx].text = 'Blocking time<t><right>%sH<t><right>%sM<t><right>%sS' % util.HoursMinsSecsFromSecs(secs)
        elif not hasattr(self, 'warnedBlockingTimeNegative'):
            self.warnedBlockingTimeNegative = True
            log.LogTraceback('Blocking time is negative?')
        self.laststats = stats
