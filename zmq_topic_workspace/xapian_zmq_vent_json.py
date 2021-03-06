# -*- coding: utf-8 -*-

import os
import sys
import time
import zmq
sys.path.append("..")
from utils import itemLine2Json
from consts import FROM_CSV, ZMQ_VENT_PORT, ZMQ_CTRL_VENT_PORT, ZMQ_SYNC_VENT_PORT, CHUNK_SIZE


if FROM_CSV:
    from consts import load_items_from_csv, CSV_INPUT_FILEPATH

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
        if count % (CHUNK_SIZE * 10) == 0:
            te = time.time()
            print 'deliver speed: %s sec/per %s' % (te - ts, CHUNK_SIZE * 10)
            if count % (CHUNK_SIZE * 100) == 0:
                print 'total deliver %s, cost: %s sec [avg: %sper/sec]' % (count, te - tb, count / (te - tb))
            ts = te
    total_cost = time.time() - tb
    return count, total_cost


if __name__ == '__main__':
    beginstr = sys.argv[1]
    endstr = sys.argv[2]
    try:
        SUBSCRIBERS =int(sys.argv[3])
    except:
        SUBSCRIBERS = 1
    context = zmq.Context()

    # Socket to send messages on
    sender = context.socket(zmq.PUSH)
    sender.bind("tcp://*:%s" % ZMQ_VENT_PORT)

    # Socket  for worker control
    controller = context.socket(zmq.PUB)
    controller.bind("tcp://*:%s" % ZMQ_CTRL_VENT_PORT)

    # Socket for sync
    syncservice = context.socket(zmq.REP)
    syncservice.bind("tcp://*:%s" % ZMQ_SYNC_VENT_PORT)

    print 'waiting', SUBSCRIBERS
    subscribers = 0
    while (subscribers < SUBSCRIBERS):
        str1 = syncservice.recv()
        syncservice.send("")
        subscribers += 1
        print 'received', subscribers
    print 'go on'
    from_csv = FROM_CSV

    def csv_input_pre_func(item):
        item = itemLine2Json(item)
        return item

    if from_csv:
        pre_funcs = [csv_input_pre_func]
        if os.path.isdir(CSV_INPUT_FILEPATH):
            count = 0
            total_cost = 0

            files_by_date = os.listdir(CSV_INPUT_FILEPATH)
            for files_a_date in files_by_date:
                print 'files_a_date', files_a_date
                if (files_a_date[:8] >= beginstr and files_a_date[:8] <= endstr):
                    time.sleep(5)
                    controller.send('%sBEGIN' % files_a_date[:8])
                    print 'sent"%sBEGIN" to workers' % files_a_date[:8]
                    files = os.listdir(os.path.join(CSV_INPUT_FILEPATH, files_a_date))
                    for f in files:
                        csv_input = load_items_from_csv(os.path.join(CSV_INPUT_FILEPATH, files_a_date ,f))
                        load_origin_data_func = csv_input.__iter__
                        tmp_count, tmp_cost = send_all(load_origin_data_func, sender, pre_funcs=pre_funcs)
                        total_cost += tmp_cost
                        count += tmp_count
                        csv_input.close()
                    controller.send('END')
                    print 'send"END" to workers'
                    print files_a_date, 'sended', 'total deliver %s, cost %s sec' % (count, total_cost)

        elif os.path.isfile(CSV_INPUT_FILEPATH):
            csv_input = load_items_from_csv(CSV_INPUT_FILEPATH)
            load_origin_data_func = csv_input.__iter__
            count, total_cost = send_all(load_origin_data_func, sender, pre_funcs=pre_funcs)
            csv_input.close()

    # send kill signal to workers
    controller.send("KILL")
    print 'send "KILL" to workers'

    # vent finished
    print 'xapian zmq vent string finished'
    print 'total deliver %s, cost %s sec' % (count, total_cost)
