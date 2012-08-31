# -*- coding: utf-8 -*-
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import wraps
from inspect import getargspec

from attest import Tests, assert_hook, raises

from energy import Energy


suite = Tests()


@contextmanager
def time_traveler(energy):
    changed_time = [datetime.fromtimestamp(0)]
    def T(timestamp=None):
        if timestamp is None:
            return changed_time[0]
        else:
            changed_time[0] = datetime.fromtimestamp(timestamp)
    def wrap(meth):
        @wraps(meth)
        def wrapped(*args, **kwargs):
            kwargs_with_now = kwargs.copy()
            kwargs_with_now['now'] = T()
            try:
                return meth(*args, **kwargs_with_now)
            except TypeError, e:
                if str(e).endswith('\'now\''):
                    return meth(*args, **kwargs)
                raise
        return wrapped
    # Patch methods that has 'now' parameter to use changed time instead of
    # real time.
    originals = {}
    for attr in dir(energy):
        val = getattr(energy, attr)
        try:
            spec = getargspec(val)
        except TypeError:
            continue
        if attr.endswith('__') or 'now' not in spec.args:
            continue
        originals[attr] = meth = val
        setattr(energy, attr, wrap(meth))
    yield energy, T
    # Revert changes
    for attr, meth in originals.iteritems():
        setattr(energy, attr, meth)


@suite.test
def init_energy():
    energy = Energy(10, 10)
    assert isinstance(energy.recovery_interval, int)
    assert energy.recovery_interval == 10
    energy = Energy(10, timedelta(seconds=10))
    assert isinstance(energy.recovery_interval, float)
    assert energy.recovery_interval == 10


@suite.test
def use_energy():
    energy = Energy(10, 1000)
    assert int(energy) == 10
    energy.use()
    assert int(energy) == 9
    energy.use(5)
    assert int(energy) == 4
    with raises(ValueError):
        energy.use(5)


@suite.test
def set_energy():
    energy = Energy(10, 1000)
    energy.set(1)
    assert int(energy) == 1
    energy.set(5)
    assert int(energy) == 5


@suite.test
def cast_energy():
    true_energy = Energy(1, 1000)
    false_energy = Energy(0, 1000)
    assert int(true_energy) == 1
    assert int(false_energy) == 0
    assert float(true_energy) == 1.0
    assert float(false_energy) == 0.0
    assert bool(true_energy) is True
    assert bool(false_energy) is False


@suite.test
def recover_energy():
    with time_traveler(Energy(10, 5)) as (energy, T):
        T( 0); energy.use(1)
        T( 1); assert int(energy) == 9;  assert energy.recover_in() == 4
        T( 2); assert int(energy) == 9;  assert energy.recover_in() == 3
        T( 3); assert int(energy) == 9;  assert energy.recover_in() == 2
        T( 4); assert int(energy) == 9;  assert energy.recover_in() == 1
        T( 5); assert int(energy) == 10; assert energy.recover_in() == 0
        T( 6); assert int(energy) == 10; assert energy.recover_in() == 0
        T(99); assert int(energy) == 10; assert energy.recover_in() == 0


@suite.test
def use_energy_while_recovering():
    with time_traveler(Energy(10, 5)) as (energy, T):
        T( 0); energy.use(5)
        T( 1); assert int(energy) == 5
        T( 2); energy.use(1)
        T( 3); assert int(energy) == 4
        T( 4); assert int(energy) == 4
        T( 5); assert int(energy) == 5
        T( 6); assert int(energy) == 5
        T( 7); energy.use(1)
        T( 8); assert int(energy) == 4
        T( 9); assert int(energy) == 4
        T(10); assert int(energy) == 5


@suite.test
def use_energy_after_recovered():
    with time_traveler(Energy(10, 5)) as (energy, T):
        T( 0); energy.use(10)
        T( 1); assert int(energy) == 0
        T( 5); energy.use(1)
        T( 6); assert int(energy) == 0


@suite.test
def use_energy_in_the_future():
    with time_traveler(Energy(10, 5)) as (energy, T):
        T( 5); energy.use()
        T( 6); assert energy.seconds_passed() == 1
        with raises(ValueError):
            T( 0); energy.seconds_passed()


@suite.test
def pickle_energy():
    try:
        import cPickle as pickle
    except ImportError:
        import pickle
    with time_traveler(Energy(10, 5)) as (energy, T):
        T( 0); assert int(energy) == 10
        T( 1); energy.use(5)
        T( 2); assert int(energy) == 5
        dump = pickle.dumps(energy)
    with time_traveler(pickle.loads(dump)) as (energy, T):
        T( 3); assert int(energy) == 5
