# -*- coding: utf-8 -*-

import os
import sys
import csv
import zmq
import time
import redis
sys.path.append("..")
from datetime import datetime
from argparse import ArgumentParser
from utils import json2csvrow
from consts import ZMQ_VENT_HOST, ZMQ_VENT_PORT, ZMQ_CTRL_VENT_PORT, ZMQ_SYNC_VENT_PORT, ZMQ_POLL_TIMEOUT, \
                   GLOBAL_CSV_QUEUE_INDEX, GLOBAL_CSV_QUEUE_SENTIMENT, GLOBAL_CSV_QUEUE_PROFILE, \
                   VENT_REDIS_HOST, VENT_REDIS_PORT, FLOW_SIZE, CSV_FLOW_PATH, GLOBAL_CSV_QUEUE_HBASE


def _default_redis(host=VENT_REDIS_HOST, port=VENT_REDIS_PORT, db=0):
    return redis.StrictRedis(host, port, db)

def get_now_csv_no(count):
    return count / FLOW_SIZE + 1


if __name__ == '__main__':
    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.connect('tcp://%s:%s' % (ZMQ_VENT_HOST, ZMQ_VENT_PORT))

    # Socket for control input
    controller = context.socket(zmq.SUB)
    controller.connect('tcp://%s:%s' % (ZMQ_VENT_HOST, ZMQ_CTRL_VENT_PORT))
    controller.setsockopt(zmq.SUBSCRIBE,"")
    print 'controller connected'

    # Socket for sync
    syncclient = context.socket(zmq.REQ)
    syncclient.connect("tcp://%s:%s" % (ZMQ_VENT_HOST, ZMQ_SYNC_VENT_PORT))

    # send sync signal
    syncclient.send("")
    str1 = syncclient.recv()
    free(str1)
    print 'ready'

    # Process messages from receiver and controller
    poller = zmq.Poller()
    poller.register(receiver, zmq.POLLIN)
    poller.register(controller, zmq.POLLIN)

    # init redis
    global_r0 = _default_redis()

    chunks = 0 # files count
    count = 0 # item count

    while 1:

        evts = poller.poll(ZMQ_POLL_TIMEOUT)
        if evts:
            socks = dict(poller.poll(ZMQ_POLL_TIMEOUT))
        else:
            socks = None
        print 'socks', socks


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
            unit_count += 1

            if unit_count % FLOW_SIZE == 0:
                print 'closed:', csv_name
                csvfile.close()
                chunks += 1
                global_r0.rpush(GLOBAL_CSV_QUEUE_INDEX, datestr + csv_name)
                global_r0.rpush(GLOBAL_CSV_QUEUE_SENTIMENT, datestr + csv_name)
                global_r0.rpush(GLOBAL_CSV_QUEUE_PROFILE, datestr + csv_name)
                global_r0.rpush(GLOBAL_CSV_QUEUE_HBASE, datestr + csv_name)
                print '%s pushed' % csv_name

                te = time.time()
                cost = te - ts
                ts = te
                print '[%s] [%s] total csv write: %s items, %s files, %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), csv_name, count, chunks, cost, CHUNK_SIZE)

                csv_no = get_now_csv_no(unit_count)
                csv_name = '%s.csv' % csv_no
                csvfile = file(os.path.join(CSV_FLOW_PATH, datestr , csv_name), 'a')
                csvwriter = csv.writer(csvfile)

        elif socks and socks.get(controller) == zmq.POLLIN:
            signal = controller.recv()
            if signal[8:] == "BEGIN": # 数据开始传输
                print 'BEGIN'
                datestr = '%s_flow/' % signal[:8]
                if not os.path.exists(CSV_FLOW_PATH + datestr):
                    os.makedirs(CSV_FLOW_PATH + datestr)
                unit_count = 0

                csv_no = get_now_csv_no(unit_count)
                csv_name = '%s.csv' % csv_no
                csvfile = file(os.path.join(CSV_FLOW_PATH, datestr , csv_name), 'a')
                csvwriter = csv.writer(csvfile)
                ts = time.time()
                tb = ts

            elif signal == "END": # 一天的数据传输结束
                print 'closed:', csv_name
                csvfile.close()
                if unit_count % FLOW_SIZE != 0:
                    chunks += 1
                    global_r0.rpush(GLOBAL_CSV_QUEUE_INDEX, datestr + csv_name)
                    global_r0.rpush(GLOBAL_CSV_QUEUE_SENTIMENT, datestr + csv_name)
                    global_r0.rpush(GLOBAL_CSV_QUEUE_PROFILE, datestr + csv_name)
                    global_r0.rpush(GLOBAL_CSV_QUEUE_HBASE, datestr + csv_name)
                    print '%s pushed' % csv_name

                te = time.time()
                cost = te - ts
                ts = te
                # print '[%s] [%s] total csv write: %s items, %s files, %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), csv_name, count, chunks, cost, FLOW_SIZE)

            elif signal == "KILL": # 全部数据传输结束
                print 'killed'
