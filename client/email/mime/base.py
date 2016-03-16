#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\email\mime\base.py
__all__ = ['MIMEBase']
from email import message

class MIMEBase(message.Message):

    def __init__(self, _maintype, _subtype, **_params):
        message.Message.__init__(self)
        ctype = '%s/%s' % (_maintype, _subtype)
        self.add_header('Content-Type', ctype, **_params)
        self['MIME-Version'] = '1.0'
