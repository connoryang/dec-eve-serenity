#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markers.py
import sys
import blue
import bluepy
GetCurrent = blue.pyos.taskletTimer.GetCurrent
ClockThis = sys.ClockThis

def Mark(context, function, *args, **kw):
    return ClockThis(context, function, *args, **kw)


def PushMark(context):
    return bluepy.PushTimer(context)


PopMark = bluepy.PopTimer
