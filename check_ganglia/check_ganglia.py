#!/usr/bin/python

import os
import sys
import optparse
import socket
import cStringIO as StringIO

import lxml.etree as ET

import nagios
from constants import *
from errors import *
from checkval import checkval
import gmond

DEFAULT_GMETAD_QUERY_PORT = 8652
DEFAULT_GMOND_PORT = 8649

def parse_args():
    p = nagios.OptionParser()

    p.add_option('-g', '--ganglia-server', default='localhost',
            help='Address of gmond/gmetad host.')
    p.add_option('-H', '--host',
            help='Host for which we want metrics.')
    p.add_option('-l', '--list', action='store_true')
    p.add_option('-m', '--metric')
    p.add_option('--query', action='store_true',
            help='Use gmetad query interface instead of gmond.')
    p.add_option('--cluster',
            help='Cluster name for gmetad query.')
    p.add_option('-x', '--extra-metrics', action='append',
            default=[])
    p.add_option('-M', '--missing', default='UNKNOWN',
            help='Exit status on missing host or metric.')
    p.add_option('-o', '--okay')
    p.add_option('-p', '--port')
    p.add_option('-t', '--timing', default='1')

    opts, args = p.parse_args();

    try:
        missing = STATUS.index(opts.missing)
    except ValueError:
        nagios.result(opts.host, STATUS_WTF,
                'Unknown exit status for -m: %s' % opts.missing)

    opts.missing = missing

    return (opts, args)

def process_ganglia_results (opts, s):
    buffer = StringIO.StringIO()
    while True:
        data = s.recv(1024)
        if not data:
            break

        buffer.write(data)

    buffer.seek(0)
    doc = ET.parse(buffer)

    try:
        host = gmond.Host(doc.find('//HOST[@NAME="%s"]' % opts.host))
    except ValueError:
        raise NoSuchHost(opts.host)

    return host

def read_gmetad_state (opts):
    '''Connect to gmetad, query for the status of a particular
    host, and return the parsed XML tree.'''

    port = opts.port or DEFAULT_GMETAD_QUERY_PORT
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((opts.ganglia_server, port))

    s.send('/%s/%s\n' % (opts.cluster, opts.host))
    return process_ganglia_results(opts, s)

def read_gmond_state (opts):
    '''Connect to gmond, read the status information, and
    return the parsed XML tree.'''

    port = opts.port or DEFAULT_GMOND_PORT
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((opts.ganglia_server, port))

    return process_ganglia_results(opts, s)

def list_metrics(host):
    '''List all the available metrics for the given host.'''

    for metric in host.metrics():
        print '%-30s %s' % (
            '%s (%s, %s)' % (
                metric.get('NAME'),
                metric.get('TYPE'),
                metric.get('UNITS')),
                metric.get('VAL'))

def check_metric (opts, host):
    '''Look up the given metric and check it against the provided warning
    and critical thresholds.'''

    xtra = []

    try:
        v = host[opts.metric]
        for m in opts.extra_metrics:
            xtra.append((m, host[m]))
    except KeyError, detail:
        raise NoSuchMetric(detail)

    status = (STATUS_CRITICAL, STATUS_WARN, STATUS_OKAY)
    for s,r in enumerate((opts.critical, opts.warn, opts.okay)):
        if r is not None and checkval(v,r):
            return (status[s], v)

    return (STATUS_OKAY, v, xtra)

def main():
    opts, args = parse_args()
    
    try:
        if opts.host is None:
            raise UsageError('No host argument.')

        for x in range(0, int(opts.timing)):
            if opts.query:
                host = read_gmetad_state(opts)
            else:
                host = read_gmond_state(opts)

        if opts.list:
            list_metrics(host)
            sys.exit(STATUS_OKAY)
        else:
            state, val, xtra = check_metric(opts, host)
            nagios.result(opts.metric, state,
                    msg='%s' % (val),
                    perfdata=([(opts.metric, val)] + xtra))

    except UsageError, detail:
        nagios.result(opts.host, STATUS_WTF, str(detail))
    except socket.error, detail:
        nagios.result(opts.host, STATUS_WTF, str(detail))
    except (NoSuchHost, NoSuchMetric), detail:
        nagios.result(opts.host, opts.missing, str(detail))

if __name__ == '__main__':
    main()

