#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\ioutils.py
import threading as _threading
import time as _time
import socket as _socket
EPHEMERAL_PORT_RANGE = (49152, 65535)

class Timeout(_socket.timeout, Exception):
    pass


class retry(object):

    def __init__(self, attempts = 2, excfilter = (Exception,), wait = 0, backoff = 1, sleepfunc = None):
        if attempts < 1:
            raise ValueError('attempts must be greater than or equal to 1.')
        if wait < 0:
            raise ValueError('wait must be greater than or equal to 0.')
        if backoff < 1:
            raise ValueError('backoff must be greater than or equal to 1.')
        self.attempts = attempts
        self.excFilter = excfilter
        self.wait = wait
        self.backoff = backoff
        self.sleep = sleepfunc or _time.sleep

    def __call__(self, func):
        attemptsLeft = [self.attempts]
        currDelay = [self.wait]

        def inner(*args, **kwargs):
            while True:
                if attemptsLeft[0] == 1:
                    return func(*args, **kwargs)
                attemptsLeft[0] -= 1
                try:
                    return func(*args, **kwargs)
                except self.excFilter:
                    if currDelay[0]:
                        self.sleep(currDelay[0])
                        currDelay[0] *= self.backoff
                    return inner(*args, **kwargs)

        return inner


class timeout(object):

    @classmethod
    def start_thread(cls, target):
        t = _threading.Thread(target=target)
        t.start()
        return t

    def __init__(self, timeoutSecs = 5):
        self.timeoutSecs = timeoutSecs

    def __call__(self, func):

        def wrapped(*args, **kwargs):
            innerResult = []
            innerExcRaised = []

            def inner():
                try:
                    result = func(*args, **kwargs)
                    innerResult.append(result)
                except Exception as exc:
                    innerExcRaised.append(exc)

            t = type(self).start_thread(inner)
            t.join(timeout=self.timeoutSecs)
            if innerResult:
                return innerResult[0]
            if innerExcRaised:
                raise innerExcRaised[0]
            raise Timeout

        return wrapped


def is_local_port_open(port):
    sock = _socket.socket()
    isBound = False
    try:
        sock.bind(('127.0.0.1', port))
    except _socket.error:
        isBound = True
    finally:
        sock.close()

    return not isBound
