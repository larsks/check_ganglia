#!/usr/bin/python

import sys

def checkval(v, r):
    negate = False

    if r[0] == '!':
        negate = True
        r = r[1:]

    if ',' in r:
        print '>>>', r,negate
        return negate ^ (v in r.split(','))

    if isinstance(v, str):
        return negate ^ (v == r)

    r = [x for x in (r.split(':') + [''])][:2]
    if r[0] == '':
        r[0] = float('-inf')
    if r[1] == '':
        r[1] = float('inf')

    return negate ^ ((v >= float(r[0])) and (v <= float(r[1])))

if __name__ == '__main__':
    v,r = sys.argv[1:]
    if v.isdigit():
        v = float(v)

    print v, checkval(v,r)

