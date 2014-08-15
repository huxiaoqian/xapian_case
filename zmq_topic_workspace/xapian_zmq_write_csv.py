# -*- coding: utf-8 -*-

import os
import sys
import zmq
import time
import redis
sys.path.append("..")
from datetime import datetime
from argparse import ArgumentParser
from utils import json2csvrow
from consts import ZMQ_VENT_HOST, ZMQ_VENT_PORT, ZMQ_POLL_TIMEOUT, \
                   GLOBAL_CSV_QUEUE_INDEX, GLOBAL_CSV_QUEUE_SENTIMENT, GLOBAL_CSV_QUEUE_PROFILE, \
                   VENT_REDIS_HOST, VENT_REDIS_PORT, CHUNK_SIZE, CSV_FLOW_PATH, GLOBAL_CSV_QUEUE_HBASE


def _default_redis(host=VENT_REDIS_HOST, port=VENT_REDIS_PORT, db=0):
    return redis.StrictRedis(host, port, db)


if __name__ == '__main__':
    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.connect('tcp://%s:%s' % (ZMQ_VENT_HOST, ZMQ_VENT_PORT))

    # Process messages from receiver
    poller = zmq.Poller()
    poller.register(receiver, zmq.POLLIN)

    # init redis
    global_r0 = _default_redis()

    chunks = 0 # files count
    count = 0 # item count
    ts = time.time()
    tb = ts
    csv_name = datetime.now().strftime('%Y%m%d%H-%M-%S.csv')
    import csv
    csvfile = file(os.path.join(CSV_FLOW_PATH, csv_name), 'a')
    csvwriter = csv.writer(csvfile)

    while 1:

        evts = poller.poll(ZMQ_POLL_TIMEOUT)
        if evts:
            socks = dict(poller.poll(ZMQ_POLL_TIMEOUT))
        else:
            socks = None

        if socks and socks.get(receiver) == zmq.POLLIN:
            item = receiver.recv_json()
            if not item:
		print 'not item'
                continue

            itemrow = json2csvrow(item)
            if not itemrow:
		print 'not itemrow'
                continue

            csvwriter.writerow(itemrow)

            count += 1
            if count % CHUNK_SIZE == 0:
                print 'closed:',csv_name
		csvfile.close()
                chunks += 1

                new_csv_name = datetime.now().strftime('%Y%m%d%H-%M-%S.csv')
                print 'csv_name,new_csv_name', csv_name, new_csv_name
		if new_csv_name != csv_name:
                    global_r0.rpush(GLOBAL_CSV_QUEUE_INDEX, csv_name)
                    global_r0.rpush(GLOBAL_CSV_QUEUE_SENTIMENT, csv_name)
                    global_r0.rpush(GLOBAL_CSV_QUEUE_PROFILE, csv_name)
                    global_r0.rpush(GLOBAL_CSV_QUEUE_HBASE, csv_name)
                    csv_name = new_csv_name
                csvfile = file(os.path.join(CSV_FLOW_PATH, csv_name), 'a')
                csvwriter = csv.writer(csvfile)

                te = time.time()
                cost = te - ts
                ts = te
                print '[%s] [%s] total csv write: %s items, %s files, %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), csv_name, count, chunks, cost, CHUNK_SIZE)
