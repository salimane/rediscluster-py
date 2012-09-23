from rediscluster.cluster_client import StrictRedisCluster
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

__version__ = '0.2.6'
VERSION = tuple(map(int, __version__.split('.')))

__all__ = [
    'StrictRedisCluster', 'RedisError', 'ConnectionError', 'ResponseError', 'AuthenticationError',
    'InvalidResponse', 'DataError', 'PubSubError', 'WatchError'
]
