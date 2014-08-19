# -*- coding: utf-8 -*-

import redis

# zmq poll timeout
ZMQ_POLL_TIMEOUT = 10000  # 10s

# xapian zmq poll timeout
XAPIAN_ZMQ_POLL_TIMEOUT = 100000 # 100s
XAPIAN_REMOTE_OPEN_TIMEOUT = 300000  # 300s

FLOW_SIZE = 5000000 # flow file size
CHUNK_SIZE = 10000 # file chunk size
XAPIAN_FLUSH_DB_SIZE = 10000 # xapian flush db size

# zmq vent port
ZMQ_VENT_HOST = '219.224.135.46'  # vent host
ZMQ_VENT_PORT = 5573 # vent port
ZMQ_CTRL_VENT_PORT = 5574 # control port
ZMQ_SYNC_VENT_PORT = 5575 # sync port

# xapian zmq vent port
XAPIAN_ZMQ_VENT_HOST = '219.224.135.48' # vent and control host
XAPIAN_ZMQ_VENT_PORT = 5580 # vent port
XAPIAN_ZMQ_CTRL_VENT_PORT = 5581 # control port

FROM_CSV = 1 # if read from csv
if FROM_CSV:
    def load_items_from_csv(csv_filepath):
        print 'csv file mode: read from csv %s' % csv_filepath
        csv_input = open(csv_filepath)
        return csv_input

    # csv_cut files path
    CSV_INPUT_FILEPATH = '/home/mirage/dev/cut_data/csv/'
    # csv_flow files path
    CSV_FILEPATH = '/home/ubuntu4/ljh/csv/flow/'

# path to write flow
CSV_FLOW_PATH = '/home/ubuntu4/ljh/csv/flow/'

# path to write xapian_index
XAPIAN_DB_PATH = 'master_timeline_weibo_csv'
XAPIAN_DATA_DIR = '/home/ubuntu3/ljh/csv/data/'
XAPIAN_STUB_FILE_DIR = '/home/ubuntu3/ljh/csv/stub/'

# redis config
GLOBAL_CSV_QUEUE_INDEX = 'global_vent_queue:index'
GLOBAL_CSV_QUEUE_SENTIMENT = 'global_vent_queue:sentiment'
GLOBAL_CSV_QUEUE_PROFILE = 'global_vent_queue:profile'
GLOBAL_CSV_QUEUE_HBASE = 'global_vent_queue:hbase'
GLOBAL_CSV_FILES = 'global_vent_queue:index'
VENT_REDIS_HOST = '192.168.1.4'
VENT_REDIS_PORT = 6379
REDIS_CONF_MAX_DB_NO = 16

def _default_redis(host=VENT_REDIS_HOST, port=VENT_REDIS_PORT, db=0):
    return redis.StrictRedis(host, port, db)

# xapian config
XAPIAN_INDEX_SCHEMA_VERSION = 5
XAPIAN_INDEX_LOCK_FILE = '/tmp/xapian_weibo'
XAPIAN_SEARCH_DEFAULT_SCHEMA_VERSION = 2
XAPIAN_EXTRA_FIELD = 'sentiment' # xapian extra field

