# -*- coding: UTF-8 -*-
import redis
import binascii
from rediscluster._compat import (b, iteritems, dictvalues)

class StrictRedis:
  """
  Implementation of the Redis Cluster Client using redis.StrictRedis

  This abstract class provides a Python interface to all Redis commands on the cluster of redis servers.
  and implementing how the commands are sent to and received from the cluster.
  
  """
  
  read_keys = {
    'debug' : 'debug', 'object' : 'object', 'getbit' : 'getbit',
    'get' : 'get', 'getrange' : 'getrange', 'hget' : 'hget',
    'hgetall' : 'hgetall', 'hkeys' : 'hkeys', 'hlen' : 'hlen', 'hmget' : 'hmget',
    'hvals' : 'hvals', 'lindex' : 'lindex', 'llen' : 'llen',
    'lrange' : 'lrange', 'object' : 'object',
    'scard' : 'scard', 'sismember' : 'sismember', 'smembers' : 'smembers',
    'srandmember' : 'srandmember', 'strlen' : 'strlen', 'type' : 'type',
    'zcard' : 'zcard', 'zcount' : 'zcount', 'zrange' : 'zrange', 'zrangebyscore' : 'zrangebyscore',
    'zrank' : 'zrank', 'zrevrange' : 'zrevrange', 'zrevrangebyscore' : 'zrevrangebyscore',
    'zrevrank' : 'zrevrank', 'zscore' : 'zscore',
    'mget' : 'mget', 'bitcount' : 'bitcount'
  }
  
  write_keys = {
    'append' : 'append', 'blpop' : 'blpop', 'brpop' : 'brpop', 'brpoplpush' : 'brpoplpush',
    'decr' : 'decr', 'decrby' : 'decrby', 'del' : 'del', 'exists' : 'exists', 'hexists' : 'hexists',
    'expire' : 'expire', 'expireat' : 'expireat', 'getset' : 'getset', 'hdel' : 'hdel',
    'hincrby' : 'hincrby', 'hset' : 'hset', 'hsetnx' : 'hsetnx', 'hmset' : 'hmset',
    'incr' : 'incr', 'incrby' : 'incrby', 'linsert' : 'linsert', 'lpop' : 'lpop',
    'lpush' : 'lpush', 'lpushx' : 'lpushx', 'lrem' : 'lrem', 'lset' : 'lset',
    'ltrim' : 'ltrim', 'move' : 'move',
    'persist' : 'persist', 'publish' : 'publish', 'psubscribe' : 'psubscribe', 'punsubscribe' : 'punsubscribe',
    'rpop' : 'rpop', 'rpoplpush' : 'rpoplpush', 'rpush' : 'rpush',
    'rpushx' : 'rpushx', 'sadd' : 'sadd', 'sdiff' : 'sdiff', 'sdiffstore' : 'sdiffstore',
    'set' : 'set', 'setbit' : 'setbit', 'setex' : 'setex', 'setnx' : 'setnx',
    'setrange' : 'setrange', 'sinter' : 'sinter', 'sinterstore' : 'sinterstore', 'smove' : 'smove',
    'sort' : 'sort', 'spop' : 'spop', 'srem' : 'srem', 'subscribe' : 'subscribe',
    'sunion' : 'sunion', 'sunionstore' : 'sunionstore', 'unsubscribe' : 'unsubscribe', 'unwatch' : 'unwatch',
    'watch' : 'watch', 'zadd' : 'zadd', 'zincrby' : 'zincrby', 'zinterstore' : 'zinterstore',
    'zrem' : 'zrem', 'zremrangebyrank' : 'zremrangebyrank', 'zremrangebyscore' : 'zremrangebyscore', 'zunionstore' : 'zunionstore',
    'mset' : 'mset', 'msetnx' : 'msetnx', 'rename' : 'rename', 'renamenx' : 'renamenx',
    'del' : 'del', 'delete' : 'delete', 'ttl' : 'ttl', 'flushall' : 'flushall', 'flushdb' : 'flushdb',
  }
  
  dont_hash = {
    'auth' : 'auth', 'config' : 'config',
    'monitor' : 'monitor', 'quit' : 'quit',
    'randomkey' : 'randomkey', 'shutdown' : 'shutdown',
    'slaveof' : 'slaveof', 'slowlog' : 'slowlog', 'sync' : 'sync',
    'flushall' : 'flushall', 'flushdb' : 'flushdb',
    'discard' : 'discard', 'echo' : 'echo', 'exec' : 'exec', 'multi' : 'multi',
    'config_set' : 'config_set', 'config_get' : 'config_get'
  }
  
  tag_keys = {
    'sinter' : 'sinter', 'sdiff' : 'sdiff', 'sdiffstore' : 'sdiffstore', 'sinterstore' : 'sinterstore',
    'smove' : 'smove', 'sunion' : 'sunion', 'sunionstore' : 'sunionstore',
    'zinterstore' : 'zinterstore', 'zunionstore' : 'zunionstore'
  }
  
  banned_keys = {
    'mget' : 'mget',
    'mset' : 'mset', 'msetnx' : 'msetnx', 'rename' : 'rename', 'renamenx' : 'renamenx',
  }
  
  loop_keys = {
    'keys' : 'keys',
    'save' : 'save', 'bgsave' : 'bgsave',
    'bgrewriteaof' : 'bgrewriteaof',
    'dbsize' : 'dbsize', 'info' : 'info',
    'lastsave' : 'lastsave', 'ping' : 'ping',
    'flushall' : 'flushall', 'flushdb' : 'flushdb',
    'randomkey' : 'randomkey', 'sync' : 'sync',
  }
  
  def __init__(self, cluster = {}, db = 0):
    #die when wrong server array
    if 'nodes' not in cluster or 'master_of' not in cluster:
      raise Exception("rediscluster: Please set a correct array of redis cluster.")

    self.cluster = cluster
    self.no_servers = len(cluster['master_of'])
    slaves = dictvalues(cluster['master_of'])
    self.redises = {}
    #connect to all servers
    for alias, server in iteritems(cluster['nodes']):
      try:
        self.__redis = redis.StrictRedis(host=server['host'], port=server['port'], db=db)
        sla = self.__redis.config_get('slaveof')['slaveof']
        if alias in slaves and sla == '':
          raise Exception("rediscluster: server %s:%s is not a slave." % (server['host'], server['port']))
      except Exception as e:
        try:
          self.__redis = redis.StrictRedis(host=server['host'], port=server['port'], db=db)
          sla = self.__redis.config_get('slaveof')['slaveof']
          if alias in slaves and sla == '':
            raise Exception("rediscluster: server %s:%s is not a slave." % (server['host'], server['port']))
        except Exception as e:
          #if node is slave and is down, replace its connection with its master's
          try:
            ms = [k for k, v in iteritems(cluster['master_of']) if v == alias and sla != ''][0]
          except IndexError as ie:
            ms = None
            
          if ms is not None:
            try:
              self.__redis = redis.StrictRedis(host=cluster['nodes'][ms]['host'], port=cluster['nodes'][ms]['port'], db=db)
              self.__redis.info()
            except Exception as e:
              try:
                self.__redis = redis.StrictRedis(host=cluster['nodes'][ms]['host'], port=cluster['nodes'][ms]['port'], db=db)
                self.__redis.info()
              except Exception as e:
                raise Exception("rediscluster cannot connect to: %s:%s %s" % (cluster['nodes'][ms]['host'], cluster['nodes'][ms]['port'], e))
      
          else:
            raise Exception("rediscluster cannot connect to: %s:%s %s" % (server['host'], server['port'], e))

      self.redises[alias] = self.__redis
    

  def __getattr__(self, name, *args, **kwargs):
    """    
    Magic method to handle all redis commands     
    - string name The name of the command called.
    - tuple args of supplied arguments to the command.  
    """
    def function(*args, **kwargs):
      if name not in StrictRedis.loop_keys:
        #trigger error msg on banned keys unless u're using it with tagged keys
        if name in StrictRedis.banned_keys and not isinstance(args[0], list) :
          raise Exception("rediscluster: Command %s Not Supported (each key name has its own node)" % name)

        #get the hash key depending on tags or not
        hkey = args[0]
        #take care of tagged key names for forcing multiple keys on the same node, e.g. r.set(['userinfo', "age:uid"], value)
        if isinstance(args[0], list) :
          hkey = args[0][0]
          args[0] = args[0][1]
          
        #get the node number
        node = str((abs(binascii.crc32(b(hkey)) & 0xffffffff) % self.no_servers) + 1)
        redisent = self.redises[self.cluster['default_node']]
        if name in StrictRedis.write_keys:
          redisent = self.redises['node_' + node]
        elif name in StrictRedis.read_keys:
          redisent = self.redises[self.cluster['master_of']['node_' + node]]
  
        #Execute the command on the server    
        return getattr(redisent, name)(*args, **kwargs)

      else:
        result = {}
        for alias, redisent in iteritems(self.redises):
          if name in StrictRedis.write_keys and alias not in self.cluster['master_of']:
            res = None
          else:
            res = getattr(redisent, name)(*args, **kwargs)
          
          if name == 'keys':
            result.append(res)
          else:
            result[alias] = res

        return result

    return function
