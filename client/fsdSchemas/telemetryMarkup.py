#Embedded file name: C:\jamieb_jamieb-pc_STABLE_1796\fsdSchemas\telemetryMarkup.py
from contextlib import contextmanager
try:
    import blue
    blueAvailable = True
except ImportError:
    blueAvailable = False

if blueAvailable:

    @contextmanager
    def TelemetryContext(name):
        blue.statistics.EnterZone(name)
        try:
            yield
        finally:
            blue.statistics.LeaveZone()


else:

    @contextmanager
    def TelemetryContext(name):
        yield
