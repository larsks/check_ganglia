from errors import *

class Host (object):
    def __init__ (self, host):
        if host is None:
            raise ValueError()

        self.host = host

    def __getitem__(self, m):
        metric = self.host.find('METRIC[@NAME="%s"]' % m)
        if metric is None:
            raise KeyError(m)

        v = metric.get('VAL')
        if metric.get('TYPE') != 'string':
            v = float(v)

        return v

    def metric (self, m):
        metric = self.host.find('METRIC[@NAME="%s"]' % m)
        if metric is None:
            raise KeyError(m)

        return metric

    def metrics(self):
        for metric in self.host.findall('METRIC'):
            yield metric

