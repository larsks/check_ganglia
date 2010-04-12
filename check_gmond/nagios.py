#!/usr/bin/python

import sys
import optparse

from constants import *

class OptionParser (optparse.OptionParser):

    def __init__ (self):
        optparse.OptionParser.__init__(self)

        self.add_option('-w', '--warn',
                help='Warn threshold.')
        self.add_option('-c', '--critical',
                help='Critical threshold.')
        self.add_option('-v', '--verbose', action='count',
                help='Make output more verbse.')

def result (service, status, msg=None, perfdata=None):
    text = [ '%s %s' % (service, STATUS[status])]
    if msg:
        text.append(': %s' % msg)
    if perfdata:
        text.append(' | ')
        text.append(' '.join(['%s=%s;' % x for x in perfdata]))
    print ''.join(text)
    sys.exit(status)

if __name__ == '__main__':
    p = OptionParser()
    opts, args = p.parse_args()
    result(STATUS_WTF, 'Thanks for playing.')

