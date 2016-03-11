#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveexceptions\exceptionEater.py
import logging

class ExceptionEater(object):

    def __init__(self, message = '', channel = None):
        self.message = message
        self.channel = channel

    def __enter__(self):
        pass

    def __exit__(self, eType, eVal, tb):
        if eType is not None:
            logger = None
            if self.channel:
                logger = logging.getLogger(self.channel)
            else:
                logger = logging.getLogger(__name__)
            logger.exception(self.message)
        return True
