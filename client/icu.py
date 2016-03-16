#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\icu.py


class ICUError(Exception):
    messages = {}

    def __str__(self):
        return '%s, error code: %d' % (self.args[1], self.args[0])

    def getErrorCode(self):
        return self.args[0]


class InvalidArgsError(Exception):
    pass


from icu_docs import *
