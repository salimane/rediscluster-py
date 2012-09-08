#!/usr/bin/env python -tt
import os

from rediscluster import __version__

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
long_description = f.read()
f.close()

setup(
    name='rediscluster',
    version=__version__,
    description='Python client for Cluster of Redis key-value store',
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
    keywords=['Redis Cluster', 'Redis', 'cluster of key-value store'],
    license='MIT',
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
