rediscluster-py
===============

a Python interface to a Cluster of Redis key-value store.

Project Goals
-------------

The goal is to be a drop in replacement of redis-py when you would like
to shard your data into a cluster of redis servers. rediscluster-py is
based on the awesome
`redis-py <https://github.com/andymccurdy/redis-py.git>`_ StrictRedis
Api, thus the original api commands would work without problems within
the context of a cluster of redis servers

Travis CI
---------

Currently, rediscluster-py is being tested via travis ci for python
version 2.6, 2.7 and 3.2: |Build Status|

Installation
------------

::

    $ sudo pip install rediscluster

or alternatively (you really should be using pip though):

::

    $ sudo easy_install rediscluster

From source:

::

    $ sudo python setup.py install

Running Tests
-------------

::

    $ git clone https://github.com/salimane/rediscluster-py.git
    $ cd rediscluster-py
    $ vi tests/config.py
    $ ./run_tests

Getting Started
---------------

::

    >>> import rediscluster
    >>> cluster = {
    ...          'nodes' : {
    ...                      'node_1' : {'host' : '127.0.0.1', 'port' : 63791},
    ...                      'node_2' : {'host' : '127.0.0.1', 'port' : 63792},
    ...                      'node_5' : {'host' : '127.0.0.1', 'port' : 63795},
    ...                      'node_6' : {'host' : '127.0.0.1', 'port' : 63796}
    ...                    },
    ...          'master_of' : {
    ...                          'node_1' : 'node_6', #node_6 slaveof node_1 in redis6.conf
    ...                          'node_2' : 'node_5'  #node_5 slaveof node_2 in redis5.conf
    ...                        },
    ...          'default_node' : 'node_1'
    ...     }
    >>> r = rediscluster.StrictRedisCluster(cluster=cluster, db=0)
    >>> r.set('foo', 'bar')
    True
    >>> r.get('foo')
    'bar'

Tagged keys
-----------

In order to specify your own hash key (so that related keys can all land
on a given node), you pass a list where you’d normally pass a scalar.
The first element of the list is the key to use for the hash and the
second is the real key that should be fetched/modify:

::

    >>> r.get(["userinfo", "foo"])

In that case “userinfo” is the hash key but “foo” is still the name of
the key that is fetched from the redis node that “userinfo” hashes to.

Information
-----------

-  Code: ``git clone git://github.com/salimane/rediscluster-py.git``
-  Home: http://github.com/salimane/rediscluster-py
-  Bugs: http://github.com/salimane/rediscluster-py/issues

Author
------

rediscluster-py is developed and maintained by Salimane Adjao Moustapha
(me@salimane.com). It can be found here:
http://github.com/salimane/rediscluster-py

.. |Build Status| image:: https://secure.travis-ci.org/salimane/rediscluster-py.png?branch=master
   :target: http://travis-ci.org/salimane/rediscluster-py
