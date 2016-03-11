#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\liveupdates\__init__.py
import binascii
import cStringIO
import imp
import logging
import marshal
import sys
import traceback
import yaml
logger = logging.getLogger(__name__)
EVAL = 'EVAL'
EXEC = 'EXEC'
RESPONSE_KEYS = ('stdout', 'stderr', 'eval', 'exception', 'exceptionTrace')
BASE64_KEYS = ('stdout', 'stderr', 'eval')

def makemodule(name = 'liveupdateholder'):
    m = imp.new_module(name)
    sys.modules[m.__name__] = name
    return m


def runcode(code, module, mode = None):
    if mode is None:
        mode = EXEC

    def displayhook(obj):
        global evalresult
        if obj is not None:
            evalresult = obj

    evalresult = None
    ex = None
    exceptionTrace = None
    ioOut, ioErr = cStringIO.StringIO(), cStringIO.StringIO()
    try:
        tmp = (sys.stdout, sys.stderr)
        sys.stdout, sys.stderr = ioOut, ioErr
        save_displayhook = sys.displayhook
        sys.displayhook = displayhook
        logger.info('Going to %r into %r: %r', mode, module.__name__, code)
        try:
            if mode == EXEC:
                exec code in globals(), module.__dict__
            else:
                evalresult = eval(code, globals(), module.__dict__)
        finally:
            sys.stdout, sys.stderr = tmp
            sys.displayhook = save_displayhook

    except Exception as ex:
        exceptionTrace = ''.join(traceback.format_tb(sys.exc_info()[2]))

    evalresultstr = None
    if evalresult is not None:
        module.__dict__['_'] = evalresult
        evalresultstr = str(evalresult)
    data = {'stdout': ioOut.getvalue(),
     'stderr': ioErr.getvalue()}
    if evalresultstr:
        data['eval'] = evalresultstr
    if ex:
        data['exception'] = '{}: {}'.format(ex.__class__.__name__, ex)
        data['exceptionTrace'] = exceptionTrace
    return data


def runcode_safeio(code, module, mode = None, loads = marshal.loads, doBase64 = True):
    realcode = loads(code)
    data = runcode(realcode, module, mode)
    result = dict(data)
    if doBase64:
        for k in BASE64_KEYS:
            if k in result:
                result[k] = binascii.b2a_base64(result[k])

    return result


class LiveUpdaterClientMixin(object):

    def __init__(self):
        self._module = makemodule()

    def HandlePayload(self, payload):
        logger.warn('Applying live update: %r', payload['id'])
        if 'module' in payload:
            module = __import__(payload['module'])
        else:
            module = self._module
        result = runcode_safeio(payload['script'], module, payload.get('mode'), loads=yaml.load, doBase64=False)
        logger.warn('Update %s applied. Contents:\n%s', payload['id'], result)
        if result.get('stdout'):
            logger.debug('stdout: %s', result['stdout'])
        if result.get('stderr'):
            logger.warn('stderr: %s', result['stderr'])
        if 'exceptionTrace' in result:
            logger.error('%s\n%s', result['exceptionTrace'], result['exception'])
        return result
