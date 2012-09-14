from rediscluster.client import StrictRedis
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
from redis.client import parse_info

__version__ = '0.2.2'
VERSION = tuple(map(int, __version__.split('.')))

__all__ = [
    'StrictRedis', 'RedisError', 'ConnectionError', 'ResponseError', 'AuthenticationError',
    'InvalidResponse', 'DataError', 'PubSubError', 'WatchError'
]