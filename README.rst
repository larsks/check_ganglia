===========
check_gmond
===========

:Author: Lars Kellogg-Stedman
:Email: lars@seas.harvard.edu

This is a Nagios plugin that checks values collected by gmond (part of the
Ganglia_ project).

Usage
-----

Generate a WARN status if cpu_wio is >= 30% or CRITICAL if
cpu_wio is >= 50%::

  check_gmond -H www.example.com -m cpu_wio -w 30 -c 50

Generate a WARN status if cpu_idle is < 70 or CRITICAL if cpu_idle < 50::

  check_gmond -H www.example.com -m cpu_idle -w :70 -c :50

Generate a CRITICAL status if os_relase is not "2.6.32.9-70.fc12.i686"::

  check_gmond -H www.example.com -m os_release -c "!2.6.32.9-70.fc12.i686"

.. _ganglia: http://ganglia.sourceforge.net/

