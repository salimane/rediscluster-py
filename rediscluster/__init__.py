from redis.exceptions import (
    AuthenticationError,
    ConnectionError,
    DataError,
    InvalidResponse,
    PubSubError,
    RedisError,
    ResponseError,
    WatchError,
)

from rediscluster.cluster_client import StrictRedisCluster

__version__ = '0.3.0'
VERSION = tuple(map(int, __version__.split('.')))

__all__ = [
    'StrictRedisCluster', 'RedisError', 'ConnectionError', 'ResponseError', 'AuthenticationError',
    'InvalidResponse', 'DataError', 'PubSubError', 'WatchError'
]
