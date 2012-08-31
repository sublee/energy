# -*- coding: utf-8 -*-
"""
Energy
~~~~~~

Energy system for social games such as FarmVille or The Sims Social.

>>> energy = Energy(10, recovery_interval=10)
>>> energy
<Energy 10/10>
>>> energy.use()
9
>>> energy
<Energy 9/10 recover in 00:09>

Links
`````

* `GitHub repository <http://github.com/sublee/energy>`_
* `development version
  <http://github.com/sublee/energy/zipball/master#egg=energy-dev>`_

"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='energy',
    version='0.0.1',
    license='BSD',
    author='Heungsub Lee',
    author_email='h@subl.ee',
    description='Energy system for social games',
    long_description=__doc__,
    platforms='any',
    py_modules=['energy'],
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Environment :: Console',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Games/Entertainment'],
    test_suite='energytests.suite',
    test_loader='attest:auto_reporter.test_loader',
    tests_require=['Attest'],
)
