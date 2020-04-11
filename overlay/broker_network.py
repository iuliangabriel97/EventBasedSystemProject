import redis

REDIS_SERVER_CONF = {
    'servers': {
      'main_server': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DATABASE': 0
        },
      'server2': {
          'HOST': 'localhost',
          'PORT': 16379,
          'DATABASE': 0
      }
    }
}


class RedisWrapper(object):
    shared_state = {}

    def __init__(self):
        self.__dict__ = self.shared_state

    def redis_connect(self, server_key):
        redis_server_conf = REDIS_SERVER_CONF['servers'][server_key]
        connection_pool = redis.ConnectionPool(host=redis_server_conf['HOST'], port=redis_server_conf['PORT'],
                                               db=redis_server_conf['DATABASE'])
        return redis.StrictRedis(connection_pool=connection_pool)


r_server = RedisWrapper().redis_connect(server_key='main_server')
r_server.ping()








