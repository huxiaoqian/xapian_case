# -*- coding: utf-8 -*-

import os
import sys
import zmq
import time
import redis
from datetime import datetime

VENT_REDIS_HOST = '192.168.1.3'
VENT_REDIS_PORT = 6379
GLOBAL_CSV_QUEUE_INDEX = 'global_vent_queue:index'

def _default_redis(host=VENT_REDIS_HOST, port=VENT_REDIS_PORT, db=0):
    return redis.StrictRedis(host, port, db)

if __name__ == '__main__':
    global_r0 = _default_redis()

    csvfile = os.listdir('/home/ubuntu3/huxiaoqian/case/csv_flow1/') # csv文件名序列
    for i in csvfile:
        global_r0.rpush(GLOBAL_CSV_QUEUE_INDEX, i)

