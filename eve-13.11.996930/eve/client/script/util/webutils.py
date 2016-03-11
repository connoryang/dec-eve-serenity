#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\util\webutils.py
__author__ = 'aevar'
import sys
import urllib
import utillib as util
import log

class WebUtils:

    @staticmethod
    def GetWebRequestParameters():
        details = {}
        try:
            details['s'] = util.GetServerName()
            details['language_id'] = prefs.GetValue('languageID', 'EN')
        except:
            log.LogException(toAlertSvc=0)
            sys.exc_clear()

        queryString = urllib.urlencode(details)
        return queryString
