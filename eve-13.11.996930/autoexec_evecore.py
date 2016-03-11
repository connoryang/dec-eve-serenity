#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\lib\autoexec_evecore.py
__all__ = ['SetupEveSpecificLogging', 'SetupForChina']
import log
import eveLocalization

def SetupForChina(forceEnglishIfNotChina = False):
    if boot.region == 'optic':
        eveLocalization.SetTimeDelta(28800)
        prefs.languageID = 'ZH'
    elif forceEnglishIfNotChina:
        prefs.languageID = 'EN'


globalChannelsList = ['Combat',
 'Environment',
 'Movement',
 'NPC',
 'Navigation',
 'UI',
 'Macho',
 'Update',
 'General',
 'MethodCalls',
 'Models',
 'Connection',
 'Turrets',
 'Fitting',
 'Unittest',
 'SP']

def evePostStacktraceCallback(out):
    try:
        import log
        import base
        from service import ROLE_SERVICE
        import util
        sessions = []
        for sess in base.GetSessions():
            if getattr(sess, 'userid') and not sess.role & ROLE_SERVICE:
                sessions.append(sess)

        if sessions:
            out.write('\nActive client sessions:\n\n')
            out.write('------------------------------------------------------------------------------------------------------\n')
            out.write('| userid |       role |     charid |     shipid | locationid | last remote call    | address         |\n')
            out.write('------------------------------------------------------------------------------------------------------\n')
            for sess in sessions:
                fmt = '| %6s | %10s | %10s | %10s | %10s | %19s | %15s |\n'
                try:
                    out.write(fmt % (sess.userid,
                     sess.role,
                     sess.charid,
                     sess.shipid,
                     sess.locationid,
                     util.FmtDate(sess.lastRemoteCall, 'll') if sess.lastRemoteCall is not None else 'No info on last call',
                     sess.address.split(':')[0] if sess.address is not None else 'No address'))
                except:
                    out.write('!error writing out session %s\n' % str(sess))
                    log.LogException()

            out.write('------------------------------------------------------------------------------------------------------\n')
            out.write('%s sessions total.\n' % len(sessions))
        else:
            out.write('There were no active client sessions.\n')
    except:
        log.LogException()


def EveMsgWindowStreamToMsgWindow():
    return prefs.GetValue('showExceptions', 0)


def EveUIMessage(*args):
    eve.Message(*args)


def SetupEveSpecificLogging():
    log.AddGlobalChannels(globalChannelsList)
    log.SetMsgWindowStreamToMsgWindowfunc(EveMsgWindowStreamToMsgWindow)
    log.SetStackFileNameSubPaths(('/server/', '/client/', '/proxy/', '/common/'))
    log.RegisterPostStackTraceAll(evePostStacktraceCallback)
    log.SetUiMessageFunc(EveUIMessage)
