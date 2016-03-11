#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\util\leftToRightHanded.py


def ConvertSpherical(latitude, longitude):
    return (latitude, -longitude)


exports = {'lh2rhUtil.ConvertSpherical': ConvertSpherical}
