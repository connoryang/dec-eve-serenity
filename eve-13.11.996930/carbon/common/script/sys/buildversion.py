#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\sys\buildversion.py


def GetBuildVersionAsInt():
    try:
        return int(boot.build)
    except ValueError:
        return 0
