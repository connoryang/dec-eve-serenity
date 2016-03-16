#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\debug.py
import os
FORCED_DEBUG = []

class DebugControl(object):

    def __init__(self, options, output):
        self.options = options
        self.output = output

    def should(self, option):
        return option in self.options or option in FORCED_DEBUG

    def write(self, msg):
        if self.should('pid'):
            msg = 'pid %5d: %s' % (os.getpid(), msg)
        self.output.write(msg + '\n')
        self.output.flush()

    def write_formatted_info(self, info):
        for line in info_formatter(info):
            self.write(' %s' % line)


def info_formatter(info):
    label_len = max([ len(l) for l, _d in info ])
    for label, data in info:
        if data == []:
            data = '-none-'
        if isinstance(data, (list, tuple)):
            prefix = '%*s:' % (label_len, label)
            for e in data:
                yield '%*s %s' % (label_len + 1, prefix, e)
                prefix = ''

        else:
            yield '%*s: %s' % (label_len, label, data)
