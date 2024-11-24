from redis import Redis
import os


def get_value(key):
    redis = Redis(host="server.local", password=os.environ['REDIS_PWD'], charset="utf-8", decode_responses=True)
    redis.ping()
    print('Connected to Redis Server ..... Retrieving key')
    key = redis.get(key)
    redis.close()
    return key
