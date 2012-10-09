# -*- coding: utf-8 -*-
"""
Energy
~~~~~~

Energy is a consumable and recoverable stuff in social games. It limits how far
players can advance in each session.

Players use energy to do actions like farming, housing, or social actions. Then
consumed energy will be recovered after few minutes. Recovery is the essence of
energy system. It will make players to come back to the game periodically.

In popular social games such as `FarmVille <http://www.facebook.com/FarmVille>`_
or `Zoo Invasion <http://apps.facebook.com/zooinvasion/?campaign=sublee&kt_st1=
project&kt_st2=energy&kt_st3=pypi>`_ or `The Sims Social <http://www.facebook.
com/TheSimsSocial>`_, this system drives high retention rate.

>>> energy = Energy(10, recovery_interval=300)
>>> print energy
<Energy 10/10>
>>> energy.use()
>>> print energy
<Energy 9/10 recover in 05:00>

Links
`````

* `GitHub repository <http://github.com/sublee/energy>`_
* `development version
  <http://github.com/sublee/energy/zipball/master#egg=energy-dev>`_

"""
from setuptools import setup

import energy


setup(
    name=energy.__name__,
    version=energy.__version__,
    license=energy.__license__,
    author=energy.__author__,
    author_email=energy.__author_email__,
    url=energy.__url__,
    description='Energy system for social games',
    long_description=__doc__,
    platforms='any',
    py_modules=['energy'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.5',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Programming Language :: Python :: Implementation :: PyPy',
                 'Topic :: Games/Entertainment'],
    test_suite='energytests.suite',
    test_loader='attest:auto_reporter.test_loader',
    tests_require=['Attest'],
)
