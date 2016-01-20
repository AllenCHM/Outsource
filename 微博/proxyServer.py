#coding=utf-8
__author__ = 'AllenCHM'

from time import time
from scrapy import Request
import pymongo
import redis


class ProxyServerBase():

    def __init__(self, name, redisHost="192.168.3.133", redisPort=6379):
        self.redisDB = redis.Redis(host=redisHost, port=redisPort, db=2)
        self.keyName = u'serverName_' + name
        if not self.redisDB.llen(self.keyName):
            self.push(self.keyName, *self.lrange(u'serverName', 0, -1))

    def put(self, ip):
        self.redisDB.lpush(self.keyName, ip)

    def delete(self, ip):
        self.redisDB.lrem(self.keyName, ip)

    def get(self):
        proxyIp = self.redisDB.rpoplpush(self.keyName,self.keyName)
        return {proxyIp.split(u':')[0]:proxyIp}

    def lrange(self, key, start, stop):
        return self.redisDB.lrange(key, start, stop)

    def exists(self, name):
        return self.redisDB.exists(name)

    def push(self, name, *values):
        return self.redisDB.lpush(name, *values)




