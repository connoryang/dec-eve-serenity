#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\ccpmetrics\__init__.py
__author__ = 'jaunty'
import httplib
import requests
import json
from socket import gethostname
from time import gmtime, strftime
METRICS_SERVER = 'http://52.17.152.179'
METRICS_SERVER_PORT = '8003'

class CCPMetrics(object):

    def __init__(self, host, port, service = None):
        self.host = host
        self.port = port
        self.service = service

    def gauge(self, metric, value, secondaryValues = None, tags = None, sample_rate = 1):
        self._write_metric(metric, value, 'gauge', secondaryValues, tags, sample_rate)

    def increment(self, metric, value = 1, secondaryValues = None, tags = None, sample_rate = 1):
        self._write_metric(metric, value, 'counter', secondaryValues, tags, sample_rate)

    def decrement(self, metric, value = 1, secondaryValues = None, tags = None, sample_rate = 1):
        self._write_metric(metric, -value, 'counter', secondaryValues, tags, sample_rate)

    def histogram(self, metric, value, secondaryValues = None, tags = None, sample_rate = 1):
        self._write_metric(metric, value, 'histogram', secondaryValues, tags, sample_rate)

    def set(self, metric, value, secondaryValues = None, tags = None, sample_rate = 1):
        self._write_metric(metric, value, 'set', secondaryValues, tags, sample_rate)

    def _write_metric(self, metric, value, metric_type, secondaryValues = None, tags = None, sample_rate = 1):
        if tags is None:
            tags = {}
        http_serv = httplib.HTTPConnection(self.host, self.port)
        hostname = gethostname()
        output = json.dumps({'name': metric,
         'host': hostname,
         'timestamp': strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime()),
         'type': metric_type,
         'value': value,
         'secondarydata': secondaryValues,
         'sampling': sample_rate,
         'tags': tags,
         'service': self.service})
        requests.post('%s:%s/metrics' % (self.host, self.port), data=output)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        raise RuntimeError('Need to supply host and port')
    _, host, port = sys.argv
    cm = CCPMetrics(host, port)
    for i in xrange(15):
        cm.increment('eve_client_disconnect', tags={'ip': '111.111.111.111'})
