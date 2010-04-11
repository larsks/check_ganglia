#!/usr/bin/python

import os
import sys
import optparse
import socket
import cStringIO as StringIO

import lxml.etree as ET

import nagios
import checkval

class ApplicationError (Exception):
    pass

class UsageError (ApplicationError):
    pass
class NoSuchHost (ApplicationError):
    pass
class NoSuchMetric (ApplicationError):
    pass

def parse_args():
    p = nagios.OptionParser()

    p.add_option('-g', '--gmon', default='localhost')
    p.add_option('-H', '--host')
    p.add_option('-l', '--list', action='store_true')
    p.add_option('-m', '--metric')
    p.add_option('-M', '--missing', default='UNKNOWN',
        help='Exit status on missing host or metric.')
    p.add_option('-o', '--okay')

    opts, args = p.parse_args();

    try:
        missing = nagios.STATUS.index(opts.missing)
    except ValueError:
        nagios.result(opts.host, nagios.STATUS_WTF,
                'Unknown exit status for -m: %s' % opts.missing)

    opts.missing = missing

    return (opts, args)

def read_gmond_state (opts):
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
    for metric in host.findall('METRIC'):
        print '%-30s %s' % (
            '%s (%s, %s)' % (
                metric.get('NAME'),
                metric.get('TYPE'),
                metric.get('UNITS')),
                metric.get('VAL'))

def check_metric (opts, host):
    metric = host.find('METRIC[@NAME="%s"]' % opts.metric)
    if metric is None:
        raise NoSuchMetric(opts.metric)

    v = metric.get('VAL')
    if metric.get('TYPE') != 'string':
        v = float(v)

    status = (nagios.STATUS_CRITICAL, nagios.STATUS_WARN,
            nagios.STATUS_OKAY)

    for s,r in enumerate((opts.critical, opts.warn, opts.okay)):
        if r is not None and checkval(v,r):
            return (status[s], v)

    return (nagios.STATUS_OKAY, v)

def main():
    opts, args = parse_args()
    
    try:
        if opts.host is None:
            raise UsageError('No host argument.')

        doc = read_gmond_state(opts)
        host = doc.find('//HOST[@NAME="%s"]' % opts.host)
        if host is None:
            raise NoSuchNost(opts.host)

        if opts.list:
            list_metrics(host)
            sys.exit(nagios.STATUS_OKAY)
        else:
            state, val = check_metric(opts, host)
            nagios.result(opts.metric, state,
                    msg='%s' % (val),
                    perfdata=((opts.metric, val),))

    except UsageError, detail:
        nagios.result(opts.host, nagios.STATUS_WTF, str(detail))
    except socket.error, detail:
        nagios.result(opts.host, nagios.STATUS_WTF, str(detail))
    except (NoSuchHost, NoSuchMetric), detail:
        nagios.result(opts.host, opts.missing, str(detail))

if __name__ == '__main__':
    main()

