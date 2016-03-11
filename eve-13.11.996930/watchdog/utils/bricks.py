#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\utils\bricks.py
import sys
import collections
from .compat import queue

class SkipRepeatsQueue(queue.Queue):

    def _init(self, maxsize):
        queue.Queue._init(self, maxsize)
        self._last_item = None

    def _put(self, item):
        if item != self._last_item:
            queue.Queue._put(self, item)
            self._last_item = item
        else:
            self.unfinished_tasks -= 1

    def _get(self):
        item = queue.Queue._get(self)
        if item is self._last_item:
            self._last_item = None
        return item


class OrderedSetQueue(queue.Queue):

    def _init(self, maxsize):
        queue.Queue._init(self, maxsize)
        self._set_of_items = set()

    def _put(self, item):
        if item not in self._set_of_items:
            queue.Queue._put(self, item)
            self._set_of_items.add(item)
        else:
            self.unfinished_tasks -= 1

    def _get(self):
        item = queue.Queue._get(self)
        self._set_of_items.remove(item)
        return item


if sys.version_info >= (2, 6, 0):
    KEY, PREV, NEXT = list(range(3))

    class OrderedSet(collections.MutableSet):

        def __init__(self, iterable = None):
            self.end = end = []
            end += [None, end, end]
            self.map = {}
            if iterable is not None:
                self |= iterable

        def __len__(self):
            return len(self.map)

        def __contains__(self, key):
            return key in self.map

        def add(self, key):
            if key not in self.map:
                end = self.end
                curr = end[PREV]
                curr[NEXT] = end[PREV] = self.map[key] = [key, curr, end]

        def discard(self, key):
            if key in self.map:
                key, prev, _next = self.map.pop(key)
                prev[NEXT] = _next
                _next[PREV] = prev

        def __iter__(self):
            end = self.end
            curr = end[NEXT]
            while curr is not end:
                yield curr[KEY]
                curr = curr[NEXT]

        def __reversed__(self):
            end = self.end
            curr = end[PREV]
            while curr is not end:
                yield curr[KEY]
                curr = curr[PREV]

        def pop(self, last = True):
            if not self:
                raise KeyError('set is empty')
            key = next(reversed(self)) if last else next(iter(self))
            self.discard(key)
            return key

        def __repr__(self):
            if not self:
                return '%s()' % (self.__class__.__name__,)
            return '%s(%r)' % (self.__class__.__name__, list(self))

        def __eq__(self, other):
            if isinstance(other, OrderedSet):
                return len(self) == len(other) and list(self) == list(other)
            return set(self) == set(other)

        def __del__(self):
            self.clear()
