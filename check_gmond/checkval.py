#!/usr/bin/python

import sys

def checkval(v, r):
    '''Check the value, *v*, against the threshold, *r*.  The
    threshold can be specified using the following syntax:

    For numeric values
    ------------------

    5       -- return True if v >= 5
    3:5     -- return True if 3 <= v <= 5
    :5      -- return True if v <=5
    1,2,3   -- return True if v in (1,2,3)

    For string values
    ------------------

    foo     -- return True if v == foo
    foo,bar -- return True if v in (foo, bar)

    Negation
    --------

    You can negate a threshold expression by preceding it with '!'.  For
    example:

    !5      -- return True if v < 5
    !3:5    -- return True if v<3 || v>5
    !1,2,3  -- return True if v not in (1,2,3)

    '''

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

