# -*- coding: UTF-8 -*-
import binascii

import redis
from redis._compat import (b, iteritems, dictvalues)


class StrictRedisCluster:
    """
    Implementation of the Redis Cluster Client using redis.StrictRedis

    This abstract class provides a Python interface to all Redis commands on the cluster of redis servers.
    and implementing how the commands are sent to and received from the cluster.

    """

    _read_keys = {
        'debug': 'debug', 'getbit': 'getbit',
        'get': 'get', 'getrange': 'getrange', 'hget': 'hget',
        'hgetall': 'hgetall', 'hkeys': 'hkeys', 'hlen': 'hlen', 'hmget': 'hmget',
        'hvals': 'hvals', 'lindex': 'lindex', 'llen': 'llen',
        'lrange': 'lrange', 'object': 'object',
        'scard': 'scard', 'sismember': 'sismember', 'smembers': 'smembers',
        'srandmember': 'srandmember', 'strlen': 'strlen', 'type': 'type',
        'zcard': 'zcard', 'zcount': 'zcount', 'zrange': 'zrange', 'zrangebyscore': 'zrangebyscore',
        'zrank': 'zrank', 'zrevrange': 'zrevrange', 'zrevrangebyscore': 'zrevrangebyscore',
        'zrevrank': 'zrevrank', 'zscore': 'zscore',
        'mget': 'mget', 'bitcount': 'bitcount', 'echo': 'echo', 'debug_object': 'debug_object',
        'substr': 'substr'
    }

    _write_keys = {
        'append': 'append', 'blpop': 'blpop', 'brpop': 'brpop', 'brpoplpush': 'brpoplpush',
        'decr': 'decr', 'decrby': 'decrby', 'del': 'del', 'exists': 'exists', 'hexists': 'hexists',
        'expire': 'expire', 'expireat': 'expireat', 'getset': 'getset', 'hdel': 'hdel',
        'hincrby': 'hincrby', 'hset': 'hset', 'hsetnx': 'hsetnx', 'hmset': 'hmset',
        'incr': 'incr', 'incrby': 'incrby', 'linsert': 'linsert', 'lpop': 'lpop',
        'lpush': 'lpush', 'lpushx': 'lpushx', 'lrem': 'lrem', 'lset': 'lset',
        'ltrim': 'ltrim', 'move': 'move',
        'persist': 'persist', 'publish': 'publish', 'psubscribe': 'psubscribe', 'punsubscribe': 'punsubscribe',
        'rpop': 'rpop', 'rpoplpush': 'rpoplpush', 'rpush': 'rpush',
        'rpushx': 'rpushx', 'sadd': 'sadd', 'sdiff': 'sdiff', 'sdiffstore': 'sdiffstore',
        'set': 'set', 'setbit': 'setbit', 'setex': 'setex', 'setnx': 'setnx',
        'setrange': 'setrange', 'sinter': 'sinter', 'sinterstore': 'sinterstore', 'smove': 'smove',
        'sort': 'sort', 'spop': 'spop', 'srem': 'srem', 'subscribe': 'subscribe',
        'sunion': 'sunion', 'sunionstore': 'sunionstore', 'unsubscribe': 'unsubscribe', 'unwatch': 'unwatch',
        'watch': 'watch', 'zadd': 'zadd', 'zincrby': 'zincrby', 'zinterstore': 'zinterstore',
        'zrem': 'zrem', 'zremrangebyrank': 'zremrangebyrank', 'zremrangebyscore': 'zremrangebyscore', 'zunionstore': 'zunionstore',
        'mset': 'mset', 'msetnx': 'msetnx', 'rename': 'rename', 'renamenx': 'renamenx',
        'del': 'del', 'delete': 'delete', 'ttl': 'ttl', 'flushall': 'flushall', 'flushdb': 'flushdb',
    }

    _dont_hash = {
        'auth': 'auth', 'monitor': 'monitor', 'quit': 'quit',
        'shutdown': 'shutdown', 'slaveof': 'slaveof', 'slowlog': 'slowlog', 'sync': 'sync',
        'discard': 'discard', 'exec': 'exec', 'multi': 'multi',
    }

    _tag_keys = {
        'mget': 'mget', 'rename': 'rename', 'renamenx': 'renamenx',
        'mset': 'mset', 'msetnx': 'msetnx',
        'brpoplpush': 'brpoplpush', 'rpoplpush': 'rpoplpush',
        'sdiff': 'sdiff', 'sdiffstore': 'sdiffstore',
        'sinter': 'sinter', 'sinterstore': 'sinterstore',
        'sunion': 'sunion', 'sunionstore': 'sunionstore',
        'smove': 'smove', 'zinterstore': 'zinterstore',
        'zunionstore': 'zunionstore', 'sort': 'sort'
    }

    _loop_keys = {
        'keys': 'keys',
        'save': 'save', 'bgsave': 'bgsave',
        'bgrewriteaof': 'bgrewriteaof',
        'dbsize': 'dbsize', 'info': 'info',
        'lastsave': 'lastsave', 'ping': 'ping',
        'flushall': 'flushall', 'flushdb': 'flushdb',
        'randomkey': 'randomkey', 'sync': 'sync',
        'config_set': 'config_set', 'config_get': 'config_get',
        'time': 'time'
    }

    def __init__(self, cluster={}, db=0):
        #raise exception when wrong server hash
        if 'nodes' not in cluster or 'master_of' not in cluster:
            raise Exception(
                "rediscluster: Please set a correct array of redis cluster.")

        self.cluster = cluster
        self.no_servers = len(cluster['master_of'])
        slaves = dictvalues(cluster['master_of'])
        self.redises = {}
        #connect to all servers
        for alias, server in iteritems(cluster['nodes']):
            try:
                self.__redis = redis.StrictRedis(db=db, **server)
                sla = self.__redis.config_get('slaveof')['slaveof']
                if alias in slaves and sla == '':
                    raise redis.DataError(
                        "rediscluster: server %s is not a slave." % (server,))
            except Exception as e:
                #if node is slave and is down, replace its connection with its master's
                try:
                    ms = [k for k, v in iteritems(cluster['master_of'])
                          if v == alias and (sla != '' or cluster['nodes'][k] == cluster['nodes'][v])][0]
                except IndexError:
                    ms = None

                if ms is not None:
                    try:
                        self.__redis = redis.StrictRedis(
                            db=db, **cluster['nodes'][ms])
                        self.__redis.info()
                    except Exception as e:
                        raise redis.ConnectionError("rediscluster cannot connect to: %s %s" % (cluster['nodes'][ms], e))

                else:
                    raise redis.ConnectionError(
                        "rediscluster cannot connect to: %s %s" % (server, e))

            self.redises[alias] = self.__redis

    def __getattr__(self, name, *args, **kwargs):
        """
        Magic method to handle all redis commands
        - string name The name of the command called.
        - tuple args of supplied arguments to the command.
        """
        def function(*args, **kwargs):
            if name not in StrictRedisCluster._loop_keys:
                if name in StrictRedisCluster._tag_keys and not isinstance(args[0], list):
                    try:
                        return getattr(self, '_rc_' + name)(*args, **kwargs)
                    except AttributeError:
                        raise redis.DataError("rediscluster: Command %s Not Supported (each key name has its own node)" % name)

                #get the hash key depending on tags or not
                hkey = args[0]
                #take care of tagged key names for forcing multiple keys on the same node, e.g. r.set(['userinfo', "age:uid"], value)
                if isinstance(args[0], list):
                    hkey = args[0][0]
                    L = list(args)
                    L[0] = args[0][1]
                    args = tuple(L)

                #get the node number
                node = self._getnodenamefor(hkey)
                redisent = self.redises[self.cluster['default_node']]
                if name in StrictRedisCluster._write_keys:
                    redisent = self.redises[node]
                elif name in StrictRedisCluster._read_keys:
                    redisent = self.redises[
                        self.cluster['master_of'][node]]

                #Execute the command on the server
                return getattr(redisent, name)(*args, **kwargs)

            else:
                result = {}
                for alias, redisent in iteritems(self.redises):
                    if name in StrictRedisCluster._write_keys and alias not in self.cluster['master_of']:
                        res = None
                    else:
                        res = getattr(redisent, name)(*args, **kwargs)

                    if name == 'keys':
                        result.append(res)
                    else:
                        result[alias] = res

                return result

        return function
    
    def _getnodenamefor(self, name):
        "Return the node name where the ``name`` would land to"
        return 'node_' + str(
            (abs(binascii.crc32(b(name)) & 0xffffffff) % self.no_servers) + 1)

    def getnodefor(self, name):
        "Return the node where the ``name`` would land to"
        node = self._getnodenamefor(name)
        return {node: self.cluster['nodes'][node]}

    def __setitem__(self, name, value):
        "Set the value at key ``name`` to ``value``"
        return self.set(name, value)

    def __getitem__(self, name):
        """
        Return the value at key ``name``, raises a KeyError if the key
        doesn't exist.
        """
        value = self.get(name)
        if value:
            return value
        raise KeyError(name)

    def __delitem__(self, *names):
        "Delete one or more keys specified by ``names``"
        return self.delete(*names)

    def object(self, infotype, key):
        "Return the encoding, idletime, or refcount about the key"
        redisent = self.redises[self.cluster['master_of'][self._getnodenamefor(key)]]
        return getattr(redisent, 'object')(infotype, key)

    def _rc_brpoplpush(self, src, dst, timeout=0):
        """
        Pop a value off the tail of ``src``, push it on the head of ``dst``
        and then return it.

        This command blocks until a value is in ``src`` or until ``timeout``
        seconds elapse, whichever is first. A ``timeout`` value of 0 blocks
        forever.
        Not atomic
        """
        rpop = self.brpop(src, timeout)
        if rpop is not None:
            self.lpush(dst, rpop[1])
            return rpop[1]
        return None

    def _rc_rpoplpush(self, src, dst):
        """
        RPOP a value off of the ``src`` list and LPUSH it
        on to the ``dst`` list.  Returns the value.
        """
        rpop = self.rpop(src)
        if rpop is not None:
            self.lpush(dst, rpop)
            return rpop
        return None

    def _rc_sdiff(self, src, *args):
        """
        Returns the members of the set resulting from the difference between
        the first set and all the successive sets.
        """
        src_set = self.smembers(src)
        if src_set is not set([]):
            for key in args:
                src_set.difference_update(self.smembers(key))
        return src_set

    def _rc_sdiffstore(self, dst, src, *args):
        """
        Store the difference of sets ``src``,  ``args`` into a new
        set named ``dest``.  Returns the number of keys in the new set.
        """
        result = self.sdiff(src, *args)
        if result is not set([]):
            return self.sadd(dst, *list(result))
        return 0

    def _rc_sinter(self, src, *args):
        """
        Returns the members of the set resulting from the difference between
        the first set and all the successive sets.
        """
        src_set = self.smembers(src)
        if src_set is not set([]):
            for key in args:
                src_set.intersection_update(self.smembers(key))
        return src_set

    def _rc_sinterstore(self, dst, src, *args):
        """
        Store the difference of sets ``src``,  ``args`` into a new
        set named ``dest``.  Returns the number of keys in the new set.
        """
        result = self.sinter(src, *args)
        if result is not set([]):
            return self.sadd(dst, *list(result))
        return 0

    def _rc_smove(self, src, dst, value):
        """
        Move ``value`` from set ``src`` to set ``dst``
        not atomic
        """
        if self.srem(src, value):
            return bool(self.sadd(dst, value))
        return False

    def _rc_sunion(self, src, *args):
        """
        Returns the members of the set resulting from the union between
        the first set and all the successive sets.
        """
        src_set = self.smembers(src)
        if src_set is not set([]):
            for key in args:
                src_set.update(self.smembers(key))
        return src_set

    def _rc_sunionstore(self, dst, src, *args):
        """
        Store the union of sets ``src``,  ``args`` into a new
        set named ``dest``.  Returns the number of keys in the new set.
        """
        result = self.sunion(src, *args)
        if result is not set([]):
            return self.sadd(dst, *list(result))
        return 0

    def _rc_mset(self, mapping):
        "Sets each key in the ``mapping`` dict to its corresponding value"
        result = True
        for k, v in iteritems(mapping):
            result = True and self.set(k, v)
        return result

    def _rc_msetnx(self, mapping):
        """
        Sets each key in the ``mapping`` dict to its corresponding value if
        none of the keys are already set
        """
        for k, v in iteritems(mapping):
            if self.exists(k):
                return False
        result = True
        for k, v in iteritems(mapping):
            result = result and self.set(k, v)
        return result

    def _rc_mget(self, *args):
        """
        Returns a list of values ordered identically to ``*args``
        """
        result = []
        for key in args:
            result.append(self.get(key))
        return result
