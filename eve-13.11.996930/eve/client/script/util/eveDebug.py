#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\util\eveDebug.py


def GetCharacterName(o = None):
    if o is not None:
        return cfg.eveowners.Get(o.charID).name
    elif eve.session.charid:
        return cfg.eveowners.Get(eve.session.charid).name
    else:
        return 'no name'


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('dbg', locals())
