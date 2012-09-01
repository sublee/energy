# -*- coding: utf-8 -*-
"""
    energy
    ~~~~~~

    Energy system for social games such as FarmVille or The Sims Social.

    :copyright: (c) 2012 by Heungsub Lee
    :license: BSD, see LICENSE for more details.
"""
from datetime import datetime, timedelta
from time import mktime


__copyright__ = 'Copyright 2012 by Heungsub Lee'
__license__ = 'BSD License'
__author__ = 'Heungsub Lee'
__email__ = 'h''@''subl.ee'
__version__ = '0.0.2'
__all__ = ['Energy']


def timestamp(time=None):
    """Makes some timestamp.
    
    1. If you pass a :class:`datetime` object, it makes a timestamp from the
       argument.
    2. If you pass a timestamp(`int` or `float`), it just returns that.
    3. If you call it without parameter, it makes a timestamp from the result
       of :meth:`datetime.utcnow`.
    """
    if time is None:
        time = datetime.utcnow()
    elif isinstance(time, (int, float)):
        return int(time)
    return mktime(time.timetuple())


def total_seconds(timedelta):
    """This function is a fallback for :meth:`timedelta.total_seconds` because
    it is available from Python 2.7.
    """
    ms, s, d = timedelta.microseconds, timedelta.seconds, timedelta.days
    return (ms + (s + d * 24 * 3600) * 10**6) / 10**6


class Energy(object):
    """Energy is a consumable stuff of social gamers. Gamers use energy for
    some actions like farming, housing or any social actions. Then consumed
    energy will be recovered after few minutes.

    :param max: maximum of energy
    :param recovery_interval: an interval in seconds to recover energy. It
                              should be :type:`int`, :type:`float` or
                              :type:`timedelta`.
    :param recovery_quantity: a quantity of once energy recovery. Defaults to
                              ``1``.
    """

    def __init__(self, max, recovery_interval, recovery_quantity=1):
        if not isinstance(max, int):
            raise TypeError('max should be int')
        if not isinstance(recovery_quantity, int):
            raise TypeError('recovery_quantity should be int')
        if isinstance(recovery_interval, timedelta):
            try:
                recovery_interval = recovery_interval.total_seconds()
            except AttributeError:
                recovery_interval = total_seconds(recovery_interval)
        if not isinstance(recovery_interval, (int, float)):
            raise TypeError('recovery_interval should be number')
        #: The maximum of energy.
        self.max = max
        #: The interval in seconds to recover energy.
        self.recovery_interval = recovery_interval
        #: The quantity of once energy recovery.
        self.recovery_quantity = recovery_quantity
        #: Quantity of used energy.
        self.used = 0
        #: Datetime when using the energy first.
        self.used_at = None

    def current(self, time=None):
        """Calculates the current energy.

        :param time: the time when checking the energy. Defaults to the present
                     time in UTC.
        """
        if not self.used:
            return self.max
        current = self.max - self.used + self.recovered(time)
        return max(0, min(self.max, current))

    def use(self, quantity=1, time=None):
        """Uses the energy.

        :param quantity: quantity of energy to be used. Defaults to ``1``.
        :param time: the time when using the energy. Defaults to the present
                     time in UTC.
        """
        time = timestamp(time)
        current = self.current()
        if current < quantity:
            raise ValueError('Not enough energy')
        if current == self.max:
            self.used = quantity
            self.used_at = time
        else:
            self.used = self.max - current + self.recovered(time) + quantity
        return current - quantity

    def set(self, quantity, time=None):
        """Sets the energy to the fixed quantity.

        :param quantity: quantity of energy to be set
        :param time: the time when setting the energy. Defaults to the present
                     time in UTC.
        """
        if quantity == self.max:
            self.used = 0
            self.used_at = None
        else:
            self.use(self.current(time) - quantity)
        return quantity

    def recovered(self, time=None):
        """Calculates the recovered energy.

        :param time: the time when checking the energy. Defaults to the present
                     time in UTC.
        """
        recovery_interval = self.recovery_interval
        passed = self.passed(time)
        if passed is None:
            return 0
        return min(int(passed / recovery_interval), self.used)

    def recover_in(self, time=None):
        """Calculates seconds to the next energy recovery.

        :param time: the time when checking the energy. Defaults to the present
                     time in UTC.
        """
        passed = self.passed(time)
        if passed is None:
            return 0
        if passed / self.recovery_interval >= self.used:
            return 0
        return self.recovery_interval - (passed % self.recovery_interval)

    def passed(self, time=None):
        """Calculates the seconds passed from using the energy first.

        :param time: the time when checking the energy. Defaults to the present
                     time in UTC.
        """
        if self.used_at is None:
            return
        seconds = timestamp(time) - self.used_at
        if seconds < 0:
            raise ValueError('Used at the future (+%.2f sec)' % -seconds)
        return seconds

    def __int__(self):
        return self.current()

    def __float__(self):
        return float(int(self))

    def __nonzero__(self):
        return bool(int(self))

    def __getstate__(self):
        return (self.max, self.recovery_interval, self.recovery_quantity, \
                self.used, self.used_at)

    def __setstate__(self, state):
        self.max = state[0]
        self.recovery_interval = state[1]
        self.recovery_quantity = state[2]
        self.used = state[3]
        self.used_at = state[4]

    def __repr__(self, time=None):
        time = timestamp(time)
        current = self.current(time)
        rv = '<%s %d/%d' % (type(self).__name__, current, self.max)
        if current < self.max:
            recover_in = self.recover_in(time)
            rv += ' recover in %02d:%02d' % (recover_in / 60, recover_in % 60)
        return rv + '>'
