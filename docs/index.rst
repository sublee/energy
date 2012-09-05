Energy
======
for social games
----------------

.. module:: energy

What is energy?
~~~~~~~~~~~~~~~

Oh, you are kidding. You already know what energy is. But, just to clarify, 
energy is a concept that is consumable and recoverable in social games.
It limits how far players can advance in each session.

Players use energy to perform actions such as farming, housing, or social
interactions. Then consumed energy will be recovered after certain amount of 
time designed by the developer. Recovery is the essence of energy system.
It will make players to come back to the game periodically.

Popular social games such as `FarmVille <http://www.facebook.com/FarmVille>`_
, `Zoo Invasion <http://apps.facebook.com/zooinvasion/?campaign=sublee&kt_st1=
project&kt_st2=energy&kt_st3=docs>`_ or `The Sims Social <http://www.facebook.
com/TheSimsSocial>`_ are benefited from the system in high retention rate.

How to use?
~~~~~~~~~~~

Install via `PyPI <http://pypi.python.org/pypi/energy>`_ first:

.. sourcecode:: bash

   $ eash_install energy

What you need to implement energy system is only :class:`Energy` object. 
Maximum energy and recovery interval have to be set in seconds before use:

::

   from energy import Energy
   energy = Energy(max=10, recovery_interval=300)

The example :class:`Energy` object has 10 of maximum and will recover in every
5 minutes. When a player performs a action that requires energy just call
:meth:`Energy.use` method:

.. sourcecode:: pycon

   >>> print energy
   <Energy 10/10>
   >>> energy.use()
   >>> print energy
   <Energy 9/10 recover in 05:00>

If the player has not enough energy, it throws :exc:`ValueError`:

.. sourcecode:: pycon

   >>> print energy
   <Energy 9/10 recover in 04:12>
   >>> energy.use(10)
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "energy.py", line 104, in use
       raise ValueError('Not enough energy')
   ValueError: Not enough energy

You may want to save :class:`Energy` object within a specific player's data
in database.

An :class:`Energy` object is serializable by Pickle. If you have a key-value
storage, you can save an :class:`Energy` object with a player easily. Or,
you should prepare some columns for :attr:`Energy.used` and
:attr:`Energy.used_at` in your database to save them. Here’s an example of
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
questions or patches will be welcomed.
