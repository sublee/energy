# -*- coding: utf-8 -*-
from __future__ import with_statement
from calendar import timegm
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import partial
from time import gmtime

from pytest import raises

from energy import Energy, timestamp


@contextmanager
def time_traveler():
    import energy
    changed_time = [0]
    def T(time=None):
        if time is None:
            return changed_time[0]
        else:
            changed_time[0] = time
    original_timestamp = energy.timestamp
    energy.timestamp = partial(energy.timestamp, default_time_getter=T)
    yield T
    energy.timestamp = original_timestamp


def test_timestamp():
    _1sec = timedelta(0, 1)
    assert datetime.utcfromtimestamp(timestamp()) - datetime.utcnow() < _1sec
    assert datetime.fromtimestamp(timestamp()) - datetime.now() < _1sec
    assert timestamp() - timegm(gmtime()) < 1


def test_init_energy():
    energy = Energy(10, 10)
    assert isinstance(energy.recovery_interval, int)
    assert energy.recovery_interval == 10
    energy = Energy(10, timedelta(seconds=10))
    assert isinstance(energy.recovery_interval, (int, float))
    assert energy.recovery_interval == 10


def test_use_energy():
    energy = Energy(10, 1000)
    assert energy == 10
    energy.use()
    assert energy == 9
    energy.use(5)
    assert energy == 4
    with raises(ValueError):
        energy.use(5)
    energy.use(10, timestamp() + 10000)
    with raises(ValueError):
        energy.use(10, timestamp() + 10010)


def test_set_energy():
    energy = Energy(10, 1000)
    energy.set(1)
    assert energy == 1
    energy.set(5)
    assert energy == 5


def test_reset_energy():
    energy = Energy(10, 1000)
    energy.use(5)
    assert energy == 5
    energy.reset()
    assert energy == 10


def test_cast_energy():
    true_energy = Energy(1, 1000)
    false_energy = Energy(0, 1000)
    assert int(true_energy) == 1
    assert int(false_energy) == 0
    assert float(true_energy) == 1.0
    assert float(false_energy) == 0.0
    assert bool(true_energy) is True
    assert bool(false_energy) is False


def test_recover_energy():
    energy = Energy(10, 5)
    with time_traveler() as T:
        T(0)
        energy.use(2)
        T(1)
        assert energy == 8
        assert energy.recover_in() == 4
        assert energy.recover_fully_in() == 9
        T(2)
        assert energy == 8
        assert energy.recover_in() == 3
        assert energy.recover_fully_in() == 8
        T(3)
        assert energy == 8
        assert energy.recover_in() == 2
        assert energy.recover_fully_in() == 7
        T(4)
        assert energy == 8
        assert energy.recover_in() == 1
        assert energy.recover_fully_in() == 6
        T(5)
        assert energy == 9
        assert energy.recover_in() == 5
        assert energy.recover_fully_in() == 5
        T(9)
        assert energy == 9
        assert energy.recover_in() == 1
        assert energy.recover_fully_in() == 1
        T(10)
        assert energy == 10
        assert energy.recover_in() == None
        assert energy.recover_fully_in() == None
        T(100)
        assert energy == 10
        assert energy.recover_in() == None
        assert energy.recover_fully_in() == None


def test_use_energy_while_recovering():
    energy = Energy(10, 5)
    with time_traveler() as T:
        T( 0); energy.use(5)
        T( 1); assert energy == 5
        T( 2); energy.use(1)
        T( 3); assert energy == 4
        T( 4); assert energy == 4
        T( 5); assert energy == 5
        T( 6); assert energy == 5
        T( 7); energy.use(1)
        T( 8); assert energy == 4
        T( 9); assert energy == 4
        T(10); assert energy == 5


def test_use_energy_after_recovered():
    energy = Energy(10, 5)
    with time_traveler() as T:
        T( 0); energy.use(10)
        T( 1); assert energy == 0
        T( 5); energy.use(1)
        T( 6); assert energy == 0


def test_use_energy_at_the_future():
    energy = Energy(10, 5)
    with time_traveler() as T:
        T( 5); energy.use()
        T( 6); assert energy.passed() == 1
        with raises(ValueError):
            T( 4); energy.passed()
        with raises(ValueError):
            T( 3); energy.passed()
        with raises(ValueError):
            T( 2); energy.passed()
        with raises(ValueError):
            T( 1); energy.passed()
        with raises(ValueError):
            T( 0); energy.passed()


def test_future_tulerance():
    energy = Energy(10, 5, future_tolerance=4)
    with time_traveler() as T:
        T(5)
        energy.use()
        # used at the past
        T(6)
        assert energy.passed() == 1
        assert energy == 9
        # used at the near future
        T(4)
        assert energy.passed() == 0
        assert energy == 9
        T(3)
        assert energy.passed() == 0
        assert energy == 9
        T(2)
        assert energy.passed() == 0
        assert energy == 9
        T(1)
        assert energy.passed() == 0
        assert energy == 9
        # used at the remote future
        T(0)
        with raises(ValueError):
            energy.passed()


def test_pickle_energy():
    try:
        import cPickle as pickle
    except ImportError:
        import pickle
    energy = Energy(10, 5)
    with time_traveler() as T:
        T( 0); assert energy == 10
        T( 1); energy.use(5)
        T( 2); assert energy == 5
        dump = pickle.dumps(energy)
        loaded_energy = pickle.loads(dump)
        assert energy == loaded_energy
        T( 3); assert energy == 5
        T( 3); assert loaded_energy == 5


class OldEnergy(Energy):

    def __setstate__(self):
        return (self.max, self.recovery_interval, self.recovery_quantity,
                self.used, self.used_at)


def test_pickle_energy_compatibility():
    try:
        import cPickle as pickle
    except ImportError:
        import pickle
    energy = OldEnergy(10, 5)
    with time_traveler() as T:
        T( 0); assert energy == 10
        T( 1); energy.use(5)
        T( 2); assert energy == 5
        dump = pickle.dumps(energy)
        dump = dump.replace('energytests\nOldEnergy'.encode(),
                            'energy\nEnergy'.encode())
        loaded_energy = pickle.loads(dump)
        assert type(loaded_energy) is Energy
        T( 3); assert energy == 5
        T( 3); assert loaded_energy == 5


def test_save_and_retrieve_energy():
    energy = Energy(10, 5)
    with time_traveler() as T:
        T( 0); assert energy == 10
        T( 1); energy.use(5)
        T( 2); assert energy == 5
        T(3)
        saved = energy.used
        saved_used, saved_used_at = energy.used, energy.used_at
        T(11)
        assert energy == 7
        loaded_energy = Energy(10, 5, used=saved_used, used_at=saved_used_at)
        assert loaded_energy == 7
        assert loaded_energy == energy
        loaded_energy2 = Energy(10, 5)
        loaded_energy2.used = saved_used
        loaded_energy2.used_at = saved_used_at
        assert loaded_energy2 == 7
        assert loaded_energy2 == energy
        loaded_energy3 = object.__new__(Energy)
        loaded_energy3.__init__(10, 5, used=saved_used, used_at=saved_used_at)
        assert loaded_energy3 == 7
        assert loaded_energy3 == energy
        loaded_energy4 = object.__new__(Energy)
        loaded_energy4.used = saved_used
        loaded_energy4.used_at = saved_used_at
        loaded_energy4.__init__(10, 5, used=saved_used, used_at=saved_used_at)
        assert loaded_energy4 == 7
        assert loaded_energy4 == energy


def test_float_recovery_interval():
    energy = Energy(10, 0.5)
    with time_traveler() as T:
        T( 0); energy == 10
        T( 1); energy.use(3)
        T( 2); energy == 9
        T( 3); energy == 10


def test_equivalent_energy():
    assert Energy(10, 10) == Energy(10, 10)
    assert Energy(5, 10) != Energy(10, 10)
    e1, e2, e3 = Energy(10, 10), Energy(10, 10), Energy(8, 10)
    with time_traveler() as T:
        T(123)
        e1.use()
        e2.use()
        assert e1 == e2
        T(128)
        e1.use()
        assert e1 != e2
        assert int(e1) == int(e3)
        assert e1 != e3


def test_set_max_energy():
    energy = Energy(10, 300)
    with time_traveler() as T:
        T( 0); assert energy == 10
        T( 1); energy.max = 11
        T( 2); assert energy == 11
        T( 3); energy.use()
        T( 4); assert energy == 10
        T( 5); energy.max = 12
        T( 6); assert energy == 10
        T( 7); energy.max = 9
        T( 8); assert energy == 9
        T( 9); energy.max = 1
        T(10); assert energy == 1
        T(11); energy.max = 10
        T(12); assert energy == 10


def test_extra_energy():
    energy = Energy(10, 300)
    with time_traveler() as T:
        T(0)
        energy.set(15)
        T(1)
        assert energy == 15
        assert energy.recover_in() is None
        assert energy.recover_fully_in() is None
        T(2)
        energy.use()
        assert energy.recover_in() is None
        assert energy.recover_fully_in() is None
        T(6)
        energy.use(6)
        T(7)
        assert energy.recover_in() == 299
        assert energy.recover_fully_in() == 599
        T(8)
        assert energy.recover_in() == 298
        assert energy.recover_fully_in() == 598
        T(9)
        energy.set(15)
        assert energy.recover_in() is None
        assert energy.recover_fully_in() is None
        T(10)
        assert energy.recover_in() is None
        assert energy.recover_fully_in() is None


def test_repr_energy():
    energy = Energy(10, 300)
    with time_traveler() as T:
        T( 0); assert repr(energy) == '<Energy 10/10>'
        T( 1); energy.use()
        T( 2); assert repr(energy) == '<Energy 9/10 recover in 04:59>'


def test_compare_energy():
    energy = Energy(10, 300)
    with time_traveler() as T:
        T(0)
        assert energy == 10
        assert energy > 9
        assert 9 < energy
        assert energy < 11
        assert 11 > energy
        assert 9 < energy < 11
        assert energy <= 10
        assert energy >= 10
        assert 10 <= energy
        assert 10 >= energy
        assert 10 <= energy <= 10


def test_arithmetic_assign_energy():
    energy = Energy(10, 3)
    with time_traveler() as T:
        T( 0); energy += 10
        T( 1); assert energy == 20
        T( 2); energy -= 13
        T( 3); assert energy == 7
        T( 6); assert energy == 8
        T( 7); energy += 10
        T( 8); energy -= 10;
        T( 9); assert energy.recover_in() == 2
        T(10); assert energy.recover_in() == 1
        T(11); assert energy == 9


def test_various_used_at():
    with time_traveler() as T:
        T(2)
        energy = Energy(10, 3, used=1, used_at=1)
        assert energy == 9
        T(5)
        assert energy == 10
        T(2)
        energy = Energy(10, 3, used=1, used_at=datetime.utcfromtimestamp(1))
        assert energy == 9
        T(5)
        assert energy == 10
