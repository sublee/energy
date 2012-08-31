# -*- coding: utf-8 -*-
"""
    energy
    ~~~~~~

    Energy system for social games such as FarmVille or The Sims Social.

    :copyright: (c) 2012 by Heungsub Lee
    :license: BSD, see LICENSE for more details.
"""
from datetime import datetime, timedelta
import time


__copyright__ = 'Copyright 2012 by Heungsub Lee'
__license__ = 'BSD License'
__author__ = 'Heungsub Lee'
__email__ = 'h''@''subl.ee'
__version__ = '0.0.1'
__all__ = ['Energy']


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
            recovery_interval = recovery_interval.total_seconds()
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

    def current(self, now=None):
        """Calculates the current energy.

        :param now: a datetime when checking the energy. Defaults to
                    ``datetime.utcnow()``.
        """
        if not self.used:
            return self.max
        current = self.max - self.used + self.recovered(now)
        return max(0, min(self.max, current))

    def use(self, quantity=1, now=None):
        """Uses the energy.

        :param quantity: quantity of energy to be used. Defaults to ``1``.
        :param now: a datetime when using the energy. Defaults to
                    ``datetime.utcnow()``.
        """
        now = now or datetime.utcnow()
        current = self.current()
        if current < quantity:
            raise ValueError('Not enough energy')
        if current == self.max:
            self.used = quantity
            self.used_at = now
        else:
            self.used = self.max - current + self.recovered(now) + quantity
        return current - quantity

    def set(self, quantity, now=None):
        """Sets the energy to the fixed quantity.

        :param quantity: quantity of energy to be set
        :param now: a datetime when setting the energy. Defaults to
                    ``datetime.utcnow()``.
        """
        if quantity == self.max:
            self.used = 0
            self.used_at = None
        else:
            self.use(self.current(now) - quantity)
        return quantity

    def recovered(self, now=None):
        """Calculates the recovered energy.

        :param now: a datetime when checking the energy. Defaults to
                    ``datetime.utcnow()``.
        """
        recovery_interval = self.recovery_interval
        seconds_passed = self.seconds_passed(now)
        if seconds_passed is None:
            return 0
        return min(int(seconds_passed / recovery_interval), self.used)

    def recover_in(self, now=None):
        """Calculates seconds to the next energy recovery.

        :param now: a datetime when checking the energy. Defaults to
                    ``datetime.utcnow()``.
        """
        seconds_passed = self.seconds_passed(now)
        if seconds_passed is None:
            return 0
        recovery_interval = self.recovery_interval
        if seconds_passed / recovery_interval >= self.used:
            return 0
        return recovery_interval - (seconds_passed % self.recovery_interval)

    def seconds_passed(self, now=None):
        """Calculates seconds passed from using the energy first.

        :param now: a datetime when checking the energy. Defaults to
                    ``datetime.utcnow()``.
        """
        if not self.used_at:
            return
        now = now or datetime.utcnow()
        seconds = (now - self.used_at).total_seconds()
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
                self.used, time.mktime(self.used_at.utctimetuple()))

    def __setstate__(self, state):
        self.max = state[0]
        self.recovery_interval = state[1]
        self.recovery_quantity = state[2]
        self.used = state[3]
        self.used_at = datetime.fromtimestamp(state[4])

    def __repr__(self, now=None):
        now = now or datetime.utcnow()
        current, = self.current(now)
        rv = '<%s %d/%d' % (type(self).__name__, current, self.max)
        if current < self.max:
            recover_in = self.recover_in(now)
            rv += ' recover in %02d:%02d' % (recover_in / 60, recover_in % 60)
        return rv + '>'
