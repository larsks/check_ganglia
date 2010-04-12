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

def parse_args():
    p = nagios.OptionParser()

    p.add_option('-g', '--gmon', default='localhost')
    p.add_option('-H', '--host')
    p.add_option('-l', '--list', action='store_true')
    p.add_option('-m', '--metric')
    p.add_option('-x', '--extra-metrics', action='append',
            default=[])
    p.add_option('-M', '--missing', default='UNKNOWN',
        help='Exit status on missing host or metric.')
    p.add_option('-o', '--okay')

    opts, args = p.parse_args();

    try:
        missing = STATUS.index(opts.missing)
    except ValueError:
        nagios.result(opts.host, STATUS_WTF,
                'Unknown exit status for -m: %s' % opts.missing)

    opts.missing = missing

    return (opts, args)

def read_gmond_state (opts):
    '''Connect to gmond and parse the XML status information.'''

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((opts.gmon, 8649))

    buffer = StringIO.StringIO()
    while True:
        data = s.recv(1024)
        if not data:
            break

        buffer.write(data)

    buffer.seek(0)
    doc = ET.parse(buffer)

    return doc

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

        doc = read_gmond_state(opts)
        try:
            host = gmond.Host(doc.find('//HOST[@NAME="%s"]' % opts.host))
        except ValueError:
            raise NoSuchHost(opts.host)

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

