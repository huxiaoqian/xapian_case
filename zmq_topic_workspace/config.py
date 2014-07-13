# -*- coding: utf-8 -*-

# xapian zmq poll timeout
XAPIAN_ZMQ_POLL_TIMEOUT = 10000  # 10s

# xapian zmq vent port
XAPIAN_ZMQ_VENT_HOST = '192.168.1.3'  # vent ip
XAPIAN_ZMQ_VENT_PORT = 5573 # vent port
FROM_CSV = 1 # if read from csv

if FROM_CSV:
    def load_items_from_csv(csv_filepath):
        print 'csv file mode: read from csv %s' % csv_filepath
        csv_input = open(csv_filepath)
        return csv_input

    # simulate outside csv files path
    CSV_INPUT_FILEPATH = '/mnt/ds600/share/weibo_201309/csv/20130902/'  # if folder need /, file don't

# redis queue for flow vent
GLOBAL_CSV_QUEUE_INDEX = 'global_vent_queue:index'
GLOBAL_CSV_QUEUE_SENTIMENT = 'global_vent_queue:sentiment'
GLOBAL_CSV_QUEUE_PROFILE = 'global_vent_queue:profile'
GLOBAL_CSV_QUEUE_HBASE = 'global_vent_queue:hbase'
VENT_REDIS_HOST = '192.168.1.2'
VENT_REDIS_PORT = 6379

# csv flow path where to write csv
CHUNK_SIZE = 10000 # file chunk size
CSV_FLOW_PATH = '/mnt/ds600/share/weibo_201309/csv/flow/'
