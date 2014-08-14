# -*- coding: utf-8 -*-

import redis

# xapian config
XAPIAN_INDEX_SCHEMA_VERSION = 5
XAPIAN_INDEX_LOCK_FILE = '/tmp/xapian_weibo'
REDIS_CONF_MAX_DB_NO = 16
XAPIAN_SEARCH_DEFAULT_SCHEMA_VERSION = 2
XAPIAN_REMOTE_OPEN_TIMEOUT = 300000  # 300s
XAPIAN_ZMQ_VENT_HOST = '219.224.135.48' # vent and control host
XAPIAN_ZMQ_VENT_PORT = 5580 # vent port
XAPIAN_ZMQ_CTRL_VENT_PORT = 5581 # control port
XAPIAN_DB_PATH = 'master_timeline_weibo_csv'
XAPIAN_DATA_DIR = '/home/ubuntu3/ljh/xapian_case/data/'
XAPIAN_STUB_FILE_DIR = '/home/ubuntu3/ljh/xapian_case/stub/'
XAPIAN_ZMQ_POLL_TIMEOUT = 100000 # 10s
XAPIAN_FLUSH_DB_SIZE = 10000 # xapian flush db size
XAPIAN_EXTRA_FIELD = 'sentiment' # xapian extra field

# file vent queue
VENT_REDIS_HOST = '192.168.1.4'
VENT_REDIS_PORT = 6379
GLOBAL_CSV_FILES = 'global_vent_queue:index'

# csv data source
FROM_CSV = 1
if FROM_CSV:
    CSV_FILEPATH = '/home/mirage/dev/original_data/csv/flow/'

def _default_redis(host=VENT_REDIS_HOST, port=VENT_REDIS_PORT, db=0):
    return redis.StrictRedis(host, port, db)
