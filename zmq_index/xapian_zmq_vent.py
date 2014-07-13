# -*- coding: utf-8 -*-

import os
import zmq
import time
import redis
from datetime import datetime
from xapian_case.csv2json import itemLine2Dict
from consts import FROM_CSV, XAPIAN_ZMQ_VENT_PORT, XAPIAN_ZMQ_CTRL_VENT_PORT, \
    VENT_REDIS_HOST, VENT_REDIS_PORT, GLOBAL_CSV_FILES, _default_redis, \
    XAPIAN_FLUSH_DB_SIZE


if FROM_CSV:
    def load_items_from_csv(csv_filepath):
        print 'csv file mode: read from csv %s' % csv_filepath
        csv_input = open(csv_filepath)
        return csv_input


def send_all(load_origin_data_func, sender, pre_funcs=[]):
    count = 0
    tb = time.time()
    ts = tb
    for item in load_origin_data_func():
        if pre_funcs:
            for func in pre_funcs:
                item = func(item)
        if item is None or item == "":
            continue
        sender.send_json(item)
        count += 1
        if count % (XAPIAN_FLUSH_DB_SIZE * 10) == 0:
            te = time.time()
            print '[%s] deliver speed: %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), te - ts, XAPIAN_FLUSH_DB_SIZE * 10)
            if count % (XAPIAN_FLUSH_DB_SIZE * 100) == 0:
                print '[%s] total deliver %s, cost: %s sec [avg: %sper/sec]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), count, te - tb, count / (te - tb))
            ts = te
    total_cost = time.time() - tb
    return count, total_cost


if __name__ == '__main__':
    """
    py xapian_zmq_vent.py'
    """

    context = zmq.Context()

    # Socket to send messages on
    sender = context.socket(zmq.PUSH)
    sender.bind("tcp://*:%s" % XAPIAN_ZMQ_VENT_PORT)

    # Socket for worker control
    controller = context.socket(zmq.PUB)
    controller.bind("tcp://*:%s" % XAPIAN_ZMQ_CTRL_VENT_PORT)
    
    # init redis
    global_r0 = _default_redis()
    from_csv = FROM_CSV

    def csv_input_pre_func(item):
        item = itemLine2Dict(item)
        return item

    if from_csv:
        pre_funcs = [csv_input_pre_func]
        from consts import CSV_FILEPATH
        if os.path.isdir(CSV_FILEPATH):
            total_cost = 0
            count = 0
            tb = time.time()
            ts = tb
            while 1:
                try:
                    csv_name = global_r0.lpop(GLOBAL_CSV_FILES)
                except Exception, e:
                    print e
                    continue

                if not csv_name:
                    time.sleep(5)
                    continue

                csv_input = load_items_from_csv(os.path.join(CSV_FILEPATH, csv_name))
                load_origin_data_func = csv_input.__iter__
                tmp_count, tmp_cost = send_all(load_origin_data_func, sender, pre_funcs=pre_funcs)
                total_cost += tmp_cost
                count += tmp_count
                csv_input.close()

                if count % (XAPIAN_FLUSH_DB_SIZE * 10) == 0:
                    te = time.time()
                    print '[%s] deliver speed: %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), te - ts, XAPIAN_FLUSH_DB_SIZE * 10)
                    if count % (XAPIAN_FLUSH_DB_SIZE * 100) == 0:
                        print '[%s] total deliver index %s, cost: %s sec [avg: %sper/sec]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), count, te - tb, count / (te - tb))
                    ts = te

    # Send kill signal to workers
    controller.send("KILL")
    print 'send "KILL" to workers'

    print 'sleep to give zmq time to deliver'
    print 'total deliver %s, cost %s sec' % (count, total_cost)
    time.sleep(10)
