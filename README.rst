=============
check_ganglia
=============

:Author: Lars Kellogg-Stedman
:Email: lars@seas.harvard.edu

.. contents::

This is a Nagios plugin that checks values collected by Ganglia_.  It can
poll either ``gmond`` or use the interactive query interface provided by
``gmetad``.

License
=======

Copyright (C) 2010 Lars Kellogg-Stedman

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Options
=======

-h, --help            show this help message and exit
-w WARN, --warn=WARN  Warn threshold.
-c CRITICAL, --critical=CRITICAL
                      Critical threshold.
-v, --verbose         Make output more verbse.
-g GANGLIA_SERVER, --ganglia-server=GANGLIA_SERVER
                      Address of gmond/gmetad host.
-H HOST, --host=HOST  Host for which we want metrics.
-l, --list            List available metrics on the target host.
-m METRIC, --metric=METRIC
                      Metric to compare against threshold values.
-q, --query           Use gmetad query interface instead of gmond.
-C CLUSTER, --cluster=CLUSTER
                      Cluster name for gmetad query.
-x EXTRA_METRICS, --extra-metrics=EXTRA_METRICS
                      Additional metrics to return as performance data.
-M MISSING, --missing=MISSING
                      Exit status on connection failure, missing host or
                      missing metric (default WARN).
-p PORT, --port=PORT  Port on which to communicate w/ gmond/gmetad

Examples
========

Using gmond
-----------

Generate a WARN status if cpu_wio is >= 30% or CRITICAL if
cpu_wio is >= 50%::

  check_gmond -H www.example.com -m cpu_wio -w 30 -c 50

Generate a WARN status if cpu_idle is < 70 or CRITICAL if cpu_idle < 50::

  check_gmond -H www.example.com -m cpu_idle -w :70 -c :50

Generate a CRITICAL status if os_relase is not "2.6.32.9-70.fc12.i686"::

  check_gmond -H www.example.com -m os_release -c "!2.6.32.9-70.fc12.i686"

Using gmetad
------------

Gmetad provides an interactive query interface that allows for efficiently
fetching a subtree of the XML data.  For environments with large numbers of
hosts this offer a substantial performance advantage.

Use the ``--query`` flag to activate gmetad support.  In additional to the
parameters you provide when using gmond, you will also need to provide the
appropriate Ganglia cluster name with ``--cluster`` (``-C``).  For
example::

  check_gmond -q -C 'HPC Monitoring' \
    -H www.example.com -m cpu_wio -w 30 -c 50

If you fail to provide a cluster name or if you mistype the cluster name,
gmetad will behave essentially just like gmond -- that is, it will dump the
entire XML tree.

Fetching additional metrics
---------------------------

You can include additional metrics as performance data in the check result
using the '-x' flag.  This is useful if you are using Nagios/Icinga to
process performance data (e.g, using pnp4nagios_).

For example::

  # check_ganglia -q -C 'My cluster' -H host.example.com \
    -m cpu_wio -x cpu_idle -x cpu_aidle -x cpu_nice \
    -x cpu_user -x cpu_system
  cpu_wio OKAY: 1.8 | cpu_wio=1.8; cpu_idle=92.7; cpu_aidle=90.0;
    cpu_nice=0.0; cpu_user=1.0; cpu_system=4.5;

(Notice that the output has been wrapped here for display purposes, but
will actually show up all on one line).

.. _pnp4nagios: http://www.pnp4nagios.org/

Specifying threshold values
===========================

(This is extracted from ``check_gmond.checkval``; see the embedded
documentation for the most current version).

The arguments to the ``-w`` and ``-c`` options use the following syntax:

For numeric values
------------------

- 5       -- match if v >= 5
- 3:5     -- match if 3 <= v <= 5
- :5      -- match if v <=5
- 1,2,3   -- match if v in (1,2,3)

For string values
------------------

- foo     -- match if v == foo
- foo,bar -- match if v in (foo, bar)

Negation
--------

You can negate a threshold expression by preceding it with '!'.  For
example:

- !5      -- match if v < 5
- !3:5    -- match if v<3 || v>5
- !1,2,3  -- match if v not in (1,2,3)

.. _ganglia: http://ganglia.sourceforge.net/

