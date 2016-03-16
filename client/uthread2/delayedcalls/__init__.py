#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\uthread2\delayedcalls\__init__.py
from .. import start_tasklet, sleep_sim, sleep

def call_after_simtime_delay(tasklet_func, delay, *args, **kwargs):
    return _call_after_delay(delay, sleep_sim, tasklet_func, *args, **kwargs)


def call_after_wallclocktime_delay(tasklet_func, delay, *args, **kwargs):
    return _call_after_delay(delay, sleep, tasklet_func, *args, **kwargs)


def _call_after_delay(delay, sleep_func, tasklet_func, *args, **kwargs):

    def _worker():
        sleep_func(delay)
        tasklet_func(*args, **kwargs)

    return start_tasklet(_worker)
