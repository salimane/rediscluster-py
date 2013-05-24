rediscluster-py
===============

a Python interface to a Cluster of Redis key-value stores.

Project Goals
-------------

The goal of ``rediscluster-py``, together with `rediscluster-php <https://github.com/salimane/rediscluster-php.git>`_, 
is to have a consistent, compatible client libraries accross programming languages
when sharding among different Redis instances in a transparent, fast, and 
fault tolerant way. ``rediscluster-py`` is based on the awesome
`redis-py <https://github.com/andymccurdy/redis-py.git>`_ StrictRedis
Api, thus the original api commands would work without problems within
the context of a cluster of redis servers

Travis CI
---------

Currently, ``rediscluster-py`` is being tested via travis ci for python
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
    ...          # node names
    ...          'nodes' : { # masters
    ...                      'node_1' : {'host' : '127.0.0.1', 'port' : 63791},
    ...                      'node_2' : {'host' : '127.0.0.1', 'port' : 63792},
    ...                    }
    ...     }
    >>> r = rediscluster.StrictRedisCluster(cluster=cluster, db=0)
    >>> r.set('foo', 'bar')
    True
    >>> r.get('foo')
    'bar'

Cluster Configuration
---------------------

The cluster configuration is a hash that is mostly based on the idea of a node, which is simply a host:port pair
that points to a single redis-server instance. This is to make sure it doesn’t get tied it
to a specific host (or port).
The advantage of this is that it is easy to add or remove nodes from 
the system to adjust the capacity while the system is running.

Read Slaves & Write Masters
---------------------------

``rediscluster`` uses the master servers stored in the cluster hash passed during instantiation to auto discover
if any slave is attached to them. It then transparently relay read redis commands to slaves and writes commands to masters.

There is also support to only use masters even if read redis commands are issued, just specify it at client instantiation like :

::

    >>> r = rediscluster.StrictRedisCluster(cluster=cluster, db=0) # read redis commands are routed to slaves
    >>>
    >>> r = rediscluster.StrictRedisCluster(cluster=cluster, db=0, mastersonly=True) # read redis commands are routed to masters

Partitioning Algorithm
----------------------

``rediscluster`` doesn't used a consistent hashing like some other libraries. In order to map every given key to the appropriate Redis node, the algorithm used,
based on crc32 and modulo, is :

::
    
    (abs(binascii.crc32(<key>) & 0xffffffff) % <number of masters>) + 1


this is used to ensure some compatibility with other languages, php in particular.
A function ``getnodefor`` is provided to get the node a particular key will be/has been stored to.

::

    >>> r.getnodefor('foo')
    {'node_2': {'host': '127.0.0.1', 'port': 63792}}
    >>>     

Hash Tags
-----------

In order to specify your own hash key (so that related keys can all land 
on a given node), ``rediscluster`` allows you to pass a string  in the form "a{b}" where you’d normally pass a scalar.
The first element of the list is the key to use for the hash and the 
second is the real key that should be fetched/modify:

::

    >>> r.get("bar{foo}")
    >>>
    >>> r.mset({"bar{foo}": "bar", "foo": "foo"})
    >>>
    >>> r.mget(["bar{foo}", "foo"])

In that case “foo” is the hash key but “bar” is still the name of
the key that is fetched from the redis node that “foo” hashes to.

Multiple Keys Redis Commands
----------------------------

In the context of storing an application data accross many redis servers, commands taking multiple keys 
as arguments are harder to use since, if the two keys will hash to two different 
instances, the operation can not be performed. Fortunately, rediscluster is a little fault tolerant 
in that it still fetches the right result for those multi keys operations as far as the client is concerned.
To do so it processes the related involved redis servers at interface level.

::

    >>> r.sadd('foo', *['a1', 'a2', 'a3'])
    3
    >>> r.sadd('bar', *['b1', 'a2', 'b3'])
    3
    >>> r.sdiffstore('foobar', 'foo', 'bar')
    2
    >>> r.smembers('foobar')
    set(['a1', 'a3'])
    >>> r.getnodefor('foo')
    {'node_2': {'host': '127.0.0.1', 'port': 63792}}
    >>> r.getnodefor('bar')
    {'node_1': {'host': '127.0.0.1', 'port': 63791}}
    >>> r.getnodefor('foobar')
    {'node_2': {'host': '127.0.0.1', 'port': 63792}}
    >>> 

Redis-Sharding & Redis-Copy
---------------------------

In order to help with moving an application with a single redis server to a cluster of redis servers
that could take advantage of ``rediscluster``, i wrote `redis-sharding <https://github.com/salimane/redis-tools#redis-sharding>`_ 
and `redis-copy <https://github.com/salimane/redis-tools#redis-copy>`_

Information
-----------

-  Code: ``git clone git://github.com/salimane/rediscluster-py.git``
-  Home: http://github.com/salimane/rediscluster-py
-  Bugs: http://github.com/salimane/rediscluster-py/issues

Author
------

``rediscluster-py`` is developed and maintained by Salimane Adjao Moustapha
(me@salimane.com). It can be found here:
http://github.com/salimane/rediscluster-py

.. |Build Status| image:: https://secure.travis-ci.org/salimane/rediscluster-py.png?branch=master
   :target: http://travis-ci.org/salimane/rediscluster-py
