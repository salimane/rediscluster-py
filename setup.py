#!/usr/bin/env python
from rediscluster import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Work around mbcs bug in distutils for py3k.
# http://bugs.python.org/issue10945
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
func = lambda name, enc = ascii: {True: enc}.get(name == 'mbcs')
codecs.register(func)

with open('README.rst') as f:
    long_description = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rediscluster',
    version=__version__,
    description='a Python interface to a Cluster of Redis key-value store',
    long_description=long_description,
    url='http://github.com/salimane/rediscluster-py',
    download_url=('http://pypi.python.org/packages/source/r/rediscluster/rediscluster-%s.tar.gz' % __version__),
    install_requires=[
        'redis>=2.4.0',
        'hiredis',
    ],
    author='Salimane Adjao Moustapha',
    author_email='me@salimane.com',
    maintainer='Salimane Adjao Moustapha',
    maintainer_email='me@salimane.com',
    keywords=['rediscluster', 'redis', 'nosql', 'cluster', 'key value',
              'data store', 'sharding'],
    license=license,
    packages=['rediscluster'],
    test_suite='tests.all_tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ]
)
