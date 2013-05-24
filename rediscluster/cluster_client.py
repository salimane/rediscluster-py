# -*- coding: UTF-8 -*-
import binascii

import redis
from redis._compat import (
    b, iteritems, dictkeys, dictvalues, basestring, bytes)
from redis.client import list_or_args


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
        'substr': 'substr', 'keys': 'keys', 'randomkey': 'randomkey',
    }

    _write_keys = {
        'append': 'append', 'blpop': 'blpop', 'brpop': 'brpop', 'brpoplpush': 'brpoplpush',
        'decr': 'decr', 'decrby': 'decrby', 'del': 'del', 'exists': 'exists', 'hexists': 'hexists',
        'expire': 'expire', 'expireat': 'expireat', 'pexpire': 'pexpire', 'pexpireat': 'pexpireat', 'getset': 'getset', 'hdel': 'hdel',
        'hincrby': 'hincrby', 'hincrbyfloat': 'hincrbyfloat', 'hset': 'hset', 'hsetnx': 'hsetnx', 'hmset': 'hmset',
        'incr': 'incr', 'incrby': 'incrby', 'incrbyfloat': 'incrbyfloat', 'linsert': 'linsert', 'lpop': 'lpop',
        'lpush': 'lpush', 'lpushx': 'lpushx', 'lrem': 'lrem', 'lset': 'lset',
        'ltrim': 'ltrim', 'move': 'move', 'bitop': 'bitop',
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
        'del': 'del', 'delete': 'delete', 'ttl': 'ttl', 'pttl': 'pttl', 'flushall': 'flushall', 'flushdb': 'flushdb',
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
        'keys': 'keys', 'dbsize': 'dbsize',

        'save': 'save', 'bgsave': 'bgsave',
        'bgrewriteaof': 'bgrewriteaof',
        'dbsize': 'dbsize', 'info': 'info',
        'lastsave': 'lastsave', 'ping': 'ping',
        'flushall': 'flushall', 'flushdb': 'flushdb',
        'sync': 'sync',
        'config_set': 'config_set', 'config_get': 'config_get',
        'time': 'time', 'client_list': 'client_list'
    }

    _loop_keys_admin = {
        'save': 'save', 'bgsave': 'bgsave',
        'bgrewriteaof': 'bgrewriteaof',
        'info': 'info',
        'lastsave': 'lastsave', 'ping': 'ping',
        'flushall': 'flushall', 'flushdb': 'flushdb',
        'sync': 'sync',
        'config_set': 'config_set', 'config_get': 'config_get',
        'time': 'time', 'client_list': 'client_list'
    }

    def __init__(self, cluster={}, db=0, mastersonly=False):
        # raise exception when wrong server hash
        if 'nodes' not in cluster:
            raise Exception(
                "rediscluster: Please set a correct array of redis cluster.")

        self.cluster = cluster
        have_master_of = 'master_of' in self.cluster
        self.no_servers = len(self.cluster['master_of']) if have_master_of else len(self.cluster['nodes'])

        self.redises = {}
        redises_cons = {}
        self.cluster['slaves'] = {}

        # connect to all servers
        for alias, server in iteritems(self.cluster['nodes']):

            if have_master_of and alias not in self.cluster['master_of']:
                continue

            server_str = str(server)
            if server_str in redises_cons:
                self.redises[alias] = redises_cons[server_str]['master']
                self.redises[alias +
                             '_slave'] = redises_cons[server_str]['slave']
                self.cluster['slaves'][alias +
                                       '_slave'] = redises_cons[server_str]['slave_node']
            else:
                try:
                    # connect to master
                    self.__redis = redis.StrictRedis(db=db, **server)
                    if not mastersonly and not have_master_of:
                        info = self.__redis.info()
                        if info['role'] != 'master':
                            raise redis.DataError(
                                "rediscluster: server %s is not a master." % (server,))

                    self.redises[alias] = self.__redis
                    redises_cons[server_str] = {}
                    redises_cons[server_str]['master'] = self.redises[alias]

                    # connect to slave
                    slave_connected = False
                    slave = {}
                    if not mastersonly:
                        if have_master_of:
                            slave = self.cluster[
                                'nodes'][self.cluster['master_of'][alias]]
                        elif 'connected_slaves' in info and info['connected_slaves'] > 0:
                            slave_host, slave_port, slave_online = info[
                                'slave0'].split(',')
                            if slave_online == 'online':
                                slave = {'host': slave_host, 'port': slave_port}

                    if slave :
                        try:
                            redis_slave = redis.StrictRedis(host=slave['host'], port=int(slave['port']), db=db)
                            self.redises[alias + '_slave'] = redis_slave
                            self.cluster['slaves'][alias + '_slave'] = {
                                'host': slave['host'], 'port': slave['port']}
                            redises_cons[server_str][
                                'slave'] = self.redises[alias + '_slave']
                            redises_cons[server_str]['slave_node'] = self.cluster['slaves'][alias + '_slave']
                            slave_connected = True
                        except redis.RedisError as e:
                            pass
                            # "RedisCluster cannot connect to: " + slave_host +':'+ slave_port

                    if not slave_connected:
                        self.redises[alias + '_slave'] = self.redises[alias]
                        self.cluster['slaves'][alias + '_slave'] = server
                        redises_cons[server_str][
                            'slave'] = self.redises[alias + '_slave']
                        redises_cons[server_str]['slave_node'] = self.cluster[
                            'slaves'][alias + '_slave']

                except redis.RedisError as e:
                    raise redis.ConnectionError(
                        "rediscluster cannot connect to: %s %s" % (server, e))

    def __getattr__(self, name, *args, **kwargs):
        """
        Magic method to handle all redis commands
        - string name The name of the command called.
        - tuple args of supplied arguments to the command.
        """
        def function(*args, **kwargs):
            if name not in StrictRedisCluster._loop_keys:
                # take care of hash tags
                tag_start = None
                key_type = hash_tag = ''
                # since we don't have "first item" in dict,
                # this list is needed in order to check hash_tag in mset({"a{a}": "a", "b":"b"})
                list_ht = []
                if isinstance(args[0], (basestring, bytes)):
                    key_type = 'string'
                    list_ht.append(args[0])
                else:
                    if isinstance(args[0], list):
                        key_type = 'list'
                        list_ht.append(args[0][0])
                    else:
                        key_type = 'dict'
                        list_ht = dictkeys(args[0])

                # check for hash tags
                for k in list_ht:
                    try:
                        tag_start = k.index('{')
                        hash_tag = k
                        break
                    except Exception as e:
                        tag_start = None

                # trigger error msg on tag keys unless we have hash tags e.g. "bar{zap}"
                if name in StrictRedisCluster._tag_keys and not tag_start:
                    try:
                        return getattr(self, '_rc_' + name)(*args, **kwargs)
                    except AttributeError:
                        raise redis.DataError("rediscluster: Command %s Not Supported (each key name has its own node)" % name)

                # get the hash key
                hkey = args[0]
                # take care of hash tags names for forcing multiple keys on the same node,
                # e.g. r.set("bar{zap}", "bar"), r.mget(["foo{foo}","bar"])
                if tag_start is not None:
                    L = list(args)
                    if key_type != 'string':
                        if key_type == 'list':
                            hkey = L[0][0][tag_start + 1:-1]
                            L[0][0] = L[0][0][0:tag_start]
                        else:
                            hkey = hash_tag[tag_start + 1:-1]
                            L[0][hash_tag[0:tag_start]] = L[0][hash_tag]
                            del L[0][hash_tag]
                    else:
                        hkey = L[0][tag_start + 1:-1]
                        L[0] = L[0][0:tag_start]

                    args = tuple(L)

                # get the node number
                node = self._getnodenamefor(hkey)
                if name in StrictRedisCluster._write_keys:
                    redisent = self.redises[node]
                elif name in StrictRedisCluster._read_keys:
                    redisent = self.redises[node + '_slave']
                else:
                    raise redis.DataError("rediscluster: Command %s Not Supported (each key name has its own node)" % name)

                # Execute the command on the server
                return getattr(redisent, name)(*args, **kwargs)

            else:

                # take care of keys that don't need to go through master and slaves redis servers
                if name not in self._loop_keys_admin:
                    try:
                        return getattr(self, '_rc_' + name)(*args, **kwargs)
                    except AttributeError:
                        raise redis.DataError("rediscluster: Command %s Not Supported (each key name has its own node)" % name)

                result = {}
                for alias, redisent in iteritems(self.redises):
                    if (name in StrictRedisCluster._write_keys and alias.find('_slave') >= 0) or (name in StrictRedisCluster._read_keys and alias.find('_slave') == -1):
                        res = None
                    else:
                        res = getattr(redisent, name)(*args, **kwargs)

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
        redisent = self.redises[self._getnodenamefor(key) + '_slave']
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
        args = list_or_args(src, args)
        src_set = self.smembers(args.pop(0))
        if src_set is not set([]):
            for key in args:
                src_set.difference_update(self.smembers(key))
        return src_set

    def _rc_sdiffstore(self, dst, src, *args):
        """
        Store the difference of sets ``src``,  ``args`` into a new
        set named ``dest``.  Returns the number of keys in the new set.
        """
        args = list_or_args(src, args)
        result = self.sdiff(*args)
        if result is not set([]):
            return self.sadd(dst, *list(result))
        return 0

    def _rc_sinter(self, src, *args):
        """
        Returns the members of the set resulting from the difference between
        the first set and all the successive sets.
        """
        args = list_or_args(src, args)
        src_set = self.smembers(args.pop(0))
        if src_set is not set([]):
            for key in args:
                src_set.intersection_update(self.smembers(key))
        return src_set

    def _rc_sinterstore(self, dst, src, *args):
        """
        Store the difference of sets ``src``,  ``args`` into a new
        set named ``dest``.  Returns the number of keys in the new set.
        """
        args = list_or_args(src, args)
        result = self.sinter(*args)
        if result is not set([]):
            return self.sadd(dst, *list(result))
        return 0

    def _rc_smove(self, src, dst, value):
        """
        Move ``value`` from set ``src`` to set ``dst``
        not atomic
        """
        if self.type(src) != b("set"):
            return self.smove(src + "{" + src + "}", dst, value)
        if self.type(dst) != b("set"):
            return self.smove(dst + "{" + dst + "}", src, value)
        if self.srem(src, value):
            return 1 if self.sadd(dst, value) else 0
        return 0

    def _rc_sunion(self, src, *args):
        """
        Returns the members of the set resulting from the union between
        the first set and all the successive sets.
        """
        args = list_or_args(src, args)
        src_set = self.smembers(args.pop(0))
        if src_set is not set([]):
            for key in args:
                src_set.update(self.smembers(key))
        return src_set

    def _rc_sunionstore(self, dst, src, *args):
        """
        Store the union of sets ``src``,  ``args`` into a new
        set named ``dest``.  Returns the number of keys in the new set.
        """
        args = list_or_args(src, args)
        result = self.sunion(*args)
        if result is not set([]):
            return self.sadd(dst, *list(result))
        return 0

    def _rc_mset(self, mapping):
        "Sets each key in the ``mapping`` dict to its corresponding value"
        result = True
        for k, v in iteritems(mapping):
            result = result and self.set(k, v)
        return result

    def _rc_msetnx(self, mapping):
        """
        Sets each key in the ``mapping`` dict to its corresponding value if
        none of the keys are already set
        """
        for k in dictkeys(mapping):
            if self.exists(k):
                return False

        return self._rc_mset(mapping)

    def _rc_mget(self, keys, *args):
        """
        Returns a list of values ordered identically to ``*args``
        """
        args = list_or_args(keys, args)
        result = []
        for key in args:
            result.append(self.get(key))
        return result

    def _rc_rename(self, src, dst):
        """
        Rename key ``src`` to ``dst``
        """
        if src == dst:
            return self.rename(src + "{" + src + "}", src)
        if not self.exists(src):
            return self.rename(src + "{" + src + "}", src)

        self.delete(dst)
        ktype = self.type(src)
        kttl = self.ttl(src)

        if ktype == b('none'):
            return False

        if ktype == b('string'):
            self.set(dst, self.get(src))
        elif ktype == b('hash'):
            self.hmset(dst, self.hgetall(src))
        elif ktype == b('list'):
            for k in self.lrange(src, 0, -1):
                self.rpush(dst, k)
        elif ktype == b('set'):
            for k in self.smembers(src):
                self.sadd(dst, k)
        elif ktype == b('zset'):
            for k, v in self.zrange(src, 0, -1, withscores=True):
                self.zadd(dst, v, k)

        # Handle keys with an expire time set
        kttl = -1 if kttl is None or kttl < 0 else int(kttl)
        if kttl != -1:
            self.expire(dst, kttl)

        return self.delete(src)

    def _rc_renamenx(self, src, dst):
        "Rename key ``src`` to ``dst`` if ``dst`` doesn't already exist"
        if self.exists(dst):
            return False

        return self._rc_rename(src, dst)

    def _rc_keys(self, pattern='*'):
        "Returns a list of keys matching ``pattern``"

        result = []
        for alias, redisent in iteritems(self.redises):
            if alias.find('_slave') == -1:
                continue

            result.extend(redisent.keys(pattern))

        return result

    def _rc_dbsize(self):
        "Returns the number of keys in the current database"

        result = 0
        for alias, redisent in iteritems(self.redises):
            if alias.find('_slave') == -1:
                continue

            result += redisent.dbsize()

        return result
