#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\uthread2\__init__.py
from uthread2_plugins import get_implementation
import uthread2_lib
try:
    from . import bluepyimpl
except ImportError:
    pass

impl = get_implementation()
map = impl.map
Map = map
sleep = impl.sleep
Sleep = sleep
sleep_sim = impl.sleep_sim
SleepSim = sleep_sim
start_tasklet = impl.start_tasklet
StartTasklet = start_tasklet
yield_ = impl.yield_
Yield = yield_
get_current = impl.get_current
Event = impl.Event
Semaphore = impl.Semaphore
from .delayedcalls import call_after_simtime_delay, call_after_wallclocktime_delay
