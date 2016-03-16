#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\net\crestExceptions.py
import exceptions

class CrestSessionExists(Exception):

    def __init__(self, oldProxyID = None):
        super(CrestSessionExists, self).__init__()
        self.oldProxyID = oldProxyID


class CrestSessionNeedsUsurpError(Exception):

    def __init__(self, sidToTokenMapToBlacklist):
        super(CrestSessionNeedsUsurpError, self).__init__()
        self.sidToTokenMapToBlacklist = sidToTokenMapToBlacklist


exceptions.CrestSessionExists = CrestSessionExists
exceptions.CrestSessionNeedsUsurpError = CrestSessionNeedsUsurpError
