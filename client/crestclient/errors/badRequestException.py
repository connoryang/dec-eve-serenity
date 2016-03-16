#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\crestclient\errors\badRequestException.py
from baseException import CrestClientBaseException

class BadRequestException(CrestClientBaseException):

    def __init__(self, message):
        super(BadRequestException, self).__init__(message, 400)
