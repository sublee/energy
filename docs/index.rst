Energy
======
for social games
----------------

.. module:: energy

What is energy?
~~~~~~~~~~~~~~~

Energy is a consumable and recoverable stuff in social games. It limits how far
players can advance in each session.

Players use energy to do actions like farming, housing, or social actions. Then
consumed energy will be recovered after few minutes. Recovery is the essence of
energy system. It will make players to come back to the game periodically.

In popular social games such as `FarmVille <http://www.facebook.com/FarmVille>`_
or `Zoo Invasion <http://apps.facebook.com/zooinvasion/?campaign=sublee&kt_st1=
project&kt_st2=energy&kt_st3=docs>`_ or `The Sims Social <http://www.facebook.
com/TheSimsSocial>`_, this system drives high retention rate.

How to use?
~~~~~~~~~~~

Install via `PyPI <http://pypi.python.org/pypi/energy>`_ first:

.. sourcecode:: bash

   $ eash_install energy

Or check out developement version:

.. sourcecode:: bash

   $ git clone git://github.com/sublee/energy.git

You can implement energy system using just :class:`Energy` object. It needs to
be set maximum energy and recovery interval in seconds:

::

   from energy import Energy
   energy = Energy(max=10, recovery_interval=300)

The example :class:`Energy` object has 10 as maximum and will recover in every
5 minutes. When a player does some action that needs to consume energy just
call :meth:`Energy.use` method:

.. sourcecode:: pycon

   >>> print energy
   <Energy 10/10>
   >>> energy.use()
   >>> print energy
   <Energy 9/10 recover in 05:00>

But if the player has not enough energy, it throws :exc:`ValueError`:

.. sourcecode:: pycon

   >>> print energy
   <Energy 9/10 recover in 04:12>
   >>> energy.use(10)
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "energy.py", line 104, in use
       raise ValueError('Not enough energy')
   ValueError: Not enough energy

You may want to save :class:`Energy` object bound to some player into the
database with the player data.

An :class:`Energy` object is serializable by Pickle. So if you have a key-value
storage, you can save an :class:`Energy` object with a player easily. If not,
you should prepare some columns for :attr:`Energy.used` and
:attr:`Energy.used_at` in your database and save them. Here’s a way to
save/load an :class:`Energy` object:

.. sourcecode:: pycon

   >>> MAX_ENERGY, ENERGY_RECOVERY_INTERVAL = 10, 300
   >>> energy = Energy(MAX_ENERGY, ENERGY_RECOVERY_INTERVAL)
   >>> saved_used, saved_used_at = energy.used, energy.used_at
   >>> loaded_energy = Energy(MAX_ENERGY, ENERGY_RECOVERY_INTERVAL,
   ...                        used=saved_used, used_at=saved_used_at)
   >>> loaded_energy == energy
   True

API
~~~

.. autoclass:: Energy
   :members:

Licensing and Author
~~~~~~~~~~~~~~~~~~~~

This project licensed with `BSD <http://en.wikipedia.org/wiki/BSD_licenses>`_.
See `LICENSE <https://github.com/sublee/energy/blob/master/LICENSE>`_ for the
details.

I'm `Heungsub Lee <http://subl.ee/>`_, a game developer. Any regarding
questions or patches are welcomed.
