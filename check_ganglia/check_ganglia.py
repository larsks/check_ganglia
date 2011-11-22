#!/usr/bin/python

import os
import sys
import optparse

import nagios
from constants import *
from errors import *
from checkval import checkval
import ganglia

def parse_args():
    p = nagios.OptionParser()

    p.add_option('-g', '--ganglia-server', default='localhost',
            help='Address of gmond/gmetad host.')
    p.add_option('-H', '--host',
            help='Host for which we want metrics.')
    p.add_option('-l', '--list', action='store_true',
            help='List available metrics on the target host.')
    p.add_option('-m', '--metric',
            help='Metric to compare against threshold values.')
    p.add_option('-X', '--expression',
            help='Expression to compare against threshold values.')
    p.add_option('-q', '--query', action='store_true',
            help='Use gmetad query interface instead of gmond.')
    p.add_option('-C', '--cluster',
            help='Cluster name for gmetad query.')
    p.add_option('-x', '--extra-metrics', action='append',
            help='Additional metrics to return as performance data.',
            default=[])
    p.add_option('-M', '--missing', default='WARN',
            help='Exit status on connection failure, missing '
                    'host or missing metric (default WARN).')
    p.add_option('-p', '--port',
            help='Port on which to communicate w/ gmond/gmetad')

    opts, args = p.parse_args();

    try:
        missing = STATUS.index(opts.missing)
    except ValueError:
        nagios.result(opts.host, STATUS_WTF,
                'Unknown exit status for -m: %s' % opts.missing)

    opts.missing = missing

    return (opts, args)

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
        if opts.expression:
            v = eval(opts.expression)
        else:
            v = host[opts.metric]

        for m in opts.extra_metrics:
            xtra.append((m, host[m]))
    except KeyError, detail:
        raise NoSuchMetric(detail)

    status = (STATUS_CRITICAL, STATUS_WARN)
    for s,r in enumerate((opts.critical, opts.warn)):
        if r is not None and checkval(v,r):
            return (status[s], v, xtra)

    return (STATUS_OKAY, v, xtra)

def main():
    opts, args = parse_args()
    
    try:
        if opts.host is None:
            raise UsageError('No host argument.')

        if opts.query:
            G = ganglia.Gmetad(opts.ganglia_server, opts.port,
                    opts.cluster)
        else:
            G = ganglia.Gmond(opts.ganglia_server, opts.port)

        host = G.query(opts.host)

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
    except (ConnectionError, NoSuchHost, NoSuchMetric), detail:
        nagios.result(opts.host, opts.missing, str(detail))

if __name__ == '__main__':
    main()

