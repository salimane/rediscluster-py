"Core exceptions raised by the rediscluster client"

from redis import (RedisError, AuthenticationError, ConnectionError, ResponseError, 
                   InvalidResponse, DataError, PubSubError, WatchError)

class RedisError(RedisError):
  pass


class AuthenticationError(AuthenticationError):
  pass


class ConnectionError(ConnectionError):
  pass


class ResponseError(ResponseError):
  pass


class InvalidResponse(InvalidResponse):
  pass


class DataError(DataError):
  pass


class PubSubError(PubSubError):
  pass


class WatchError(WatchError):
  pass
