import socket
import lxml.etree as ET
from cStringIO import StringIO

from errors import *

DEFAULT_GMETAD_QUERY_PORT = 8652
DEFAULT_GMOND_PORT = 8649

class Host (object):
    '''A very thing wrapper over the <HOST> element returned by
    ElementTree.'''

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

class Gmond (object):
    '''A simple class for communicating with a Ganglia gmond server.'''

    def __init__ (self, server, port=DEFAULT_GMOND_PORT):
        self.server = server
        if port is None:
            port = DEFAULT_GMOND_PORT
        self.port = port

    def query(self, host, **kwargs):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server, self.port))
        if hasattr(self, '_send_commands'):
            self._send_commands(s, host, **kwargs)
        return self.process_results(s, host)

    def process_results (self, s, host):
        buffer = StringIO()
        while True:
            data = s.recv(1024)
            if not data:
                break

            buffer.write(data)
        s.close()

        buffer.seek(0)
        doc = ET.parse(buffer)

        try:
            hostdata = Host(doc.find('//HOST[@NAME="%s"]' % host))
        except ValueError:
            raise NoSuchHost(host)

        return hostdata

class Gmetad (Gmond):
    '''A simple class for communicating with a Ganglia gmetad server.  This
    is almost exactly like the Gmond class, except it uses the Gmetad query
    interface for better performance in large installations.'''

    def __init__ (self, server, port=DEFAULT_GMETAD_QUERY_PORT, cluster=None):
        self.cluster = cluster
        if port is None:
            port = DEFAULT_GMETAD_QUERY_PORT
        super(Gmetad, self).__init__(server, port)

    def _send_commands(self, s, host=None, cluster=None):
        if cluster is None:
            cluster = self.cluster
        s.send('/%s/%s\n' % (cluster, host))

if __name__ == '__main__':
    import sys

    g1 = Gmond(sys.argv[1])
    g2 = Gmetad(sys.argv[1])
 
