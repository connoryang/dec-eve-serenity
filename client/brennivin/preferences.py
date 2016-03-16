#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\preferences.py
import json
import logging
import os
import sys
import traceback
logger = logging.getLogger(__name__)

class Preferences(object):

    def __init__(self, filename, onloaderror = None):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.prefs = {}
        self.filename = filename
        self.onloaderror = onloaderror
        self.load()

    def loader(self, fp):
        return json.load(fp)

    def dumper(self, obj, fp):
        return json.dump(obj, fp)

    def openmode(self):
        return 't'

    def get(self, region, variable, defaultValue):
        try:
            return self.prefs[region][variable]
        except KeyError:
            return defaultValue

    def set(self, region, variable, value):
        if region not in self.prefs:
            self.prefs[region] = {}
        self.prefs[region][variable] = value
        self.save()

    def setdefault(self, region, variable, defaultValue):
        sentinel = object()
        result = self.get(region, variable, sentinel)
        if result == sentinel:
            result = defaultValue
            self.set(region, variable, result)
        return result

    def save(self):
        with open(self.filename, 'w' + self.openmode()) as f:
            self.dumper(self.prefs, f)

    def load(self):
        try:
            if os.path.isfile(self.filename):
                with open(self.filename, 'r' + self.openmode()) as f:
                    self.prefs = self.loader(f)
        except Exception:
            if self.onloaderror:
                self.onloaderror(*sys.exc_info())
            else:
                logger.error(traceback.format_exc())

        if not isinstance(self.prefs, dict):
            self.prefs = {}
