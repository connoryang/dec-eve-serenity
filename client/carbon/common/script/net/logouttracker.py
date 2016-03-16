#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\net\logouttracker.py
import logging
logger = logging.getLogger(__name__)

def TrackLogOut(reason, serverIp):
    import localization
    import ccpmetrics
    try:
        cm = ccpmetrics.CCPMetrics(ccpmetrics.METRICS_SERVER, ccpmetrics.METRICS_SERVER_PORT)
        if reason == localization.GetByLabel('/Carbon/MachoNet/SocketWasClosed'):
            logger.info('sending disconnect event')
            cm.increment('eve_client_disconnect', tags={'serverIp': serverIp})
    except Exception:
        logger.exception('Failed to register disconnect')
