# -*- coding: utf-8 -*-

import os
import zmq
import sys
import time
import redis
ab_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../xapian_weibo')
sys.path.append(ab_path)

if FROM_CSV:
    from index_utils import load_items_from_csv
from index_utils import send_all
from csv2json import itemLine2Dict
from consts import FROM_CSV, XAPIAN_ZMQ_VENT_PORT, XAPIAN_ZMQ_CTRL_VENT_PORT
from config import VENT_REDIS_HOST, VENT_REDIS_PORT, GLOBAL_CSV_FIELS


def _default_redis(host=VENT_REDIS_HOST, port=VENT_REDIS_PORT, db=0):
    return redis.StrictRedis(host, port, db)


if __name__ == '__main__':
    """
    'py xapian_backend_zmq_vent.py'
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

    from consts import FROM_CSV
    from_csv = FROM_CSV

    def csv_input_pre_func(item):
        item = itemLine2Dict(item)
        return item

    if from_csv:
        pre_funcs = [csv_input_pre_func]
        from config import CSV_FLOW_PATH as CSV_FILEPATH
        if os.path.isdir(CSV_FILEPATH):
            total_cost = 0
            count = 0

            while 1:
                try:
                    csv_name = global_r0.lpop(GLOBAL_CSV_FIELS)
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

        elif os.path.isfile(CSV_FILEPATH):
            csv_input = load_items_from_csv(CSV_FILEPATH)
            load_origin_data_func = csv_input.__iter__
            count, total_cost = send_all(load_origin_data_func, sender, pre_funcs=pre_funcs)
            csv_input.close()

    # Send kill signal to workers
    controller.send("KILL")
    print 'send "KILL" to workers'

    print 'sleep to give zmq time to deliver'
    print 'total deliver %s, cost %s sec' % (count, total_cost)
    time.sleep(10)
