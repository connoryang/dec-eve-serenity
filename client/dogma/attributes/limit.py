#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\attributes\limit.py
import collections

def LimitAttributeOnItem(item, timestamp, attribute, value, length = 10):
    if item is None:
        return value
    else:
        limit = item.GetValue(attribute)
        if limit:
            try:
                history = item.rollingHistory[attribute]
            except AttributeError:
                item.rollingHistory = collections.defaultdict(collections.OrderedDict)
                history = item.rollingHistory[attribute]

            return GetRollingLimit(history, timestamp, limit, value, length)
        return value


def GetRollingLimit(history, timestamp, limit, value, length = 10):
    if limit and value:
        timestamp = int(timestamp)
        oldest = timestamp - length
        for key in history.keys():
            if key < oldest:
                del history[key]
            else:
                break

        total = sum(history.itervalues())
        limit = limit * length
        value = min(value, max(limit - total, 0))
        if value == 0:
            return 0
        history[timestamp] = value + history.get(timestamp, 0)
    return value
