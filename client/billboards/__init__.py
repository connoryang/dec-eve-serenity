#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\billboards\__init__.py
from billboardsystem import BillboardSystem

def get_billboard_system():
    try:
        return get_billboard_system._system
    except AttributeError:
        system = BillboardSystem()
        get_billboard_system._system = system
        return system
