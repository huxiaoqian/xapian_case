# -*- coding: utf-8 -*-

import os
import sys
import zmq
import time
sys.path.append("..")
from datetime import datetime
from argparse import ArgumentParser
from xapian_case.utils import load_scws, cut
from xapian_index import XapianIndex
from consts import XAPIAN_INDEX_SCHEMA_VERSION, XAPIAN_ZMQ_VENT_HOST, \
    XAPIAN_ZMQ_VENT_PORT, XAPIAN_ZMQ_CTRL_VENT_PORT, XAPIAN_DB_PATH, \
    XAPIAN_ZMQ_POLL_TIMEOUT, XAPIAN_FLUSH_DB_SIZE, XAPIAN_ZMQ_SYNC_VENT_PORT, \
    XAPIAN_DATA_DIR, XAPIAN_EXTRA_FIELD
from triple_sentiment_classifier import triple_classifier

SCHEMA_VERSION = XAPIAN_INDEX_SCHEMA_VERSION

if __name__ == '__main__':
    """
    py xapian_zmq_work.py
    """

    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.connect('tcp://%s:%s' % (XAPIAN_ZMQ_VENT_HOST, XAPIAN_ZMQ_VENT_PORT))

    # Socket for control input
    controller = context.socket(zmq.SUB)
    controller.connect('tcp://%s:%s' % (XAPIAN_ZMQ_VENT_HOST, XAPIAN_ZMQ_CTRL_VENT_PORT))
    controller.setsockopt(zmq.SUBSCRIBE, "")

    # Socket for sync
    syncclient = context.socket(zmq.REQ)
    syncclient.connect("tcp://%s:%s" % (XAPIAN_ZMQ_VENT_HOST, XAPIAN_ZMQ_SYNC_VENT_PORT))

    # send sync signal
    syncclient.send("")
    str1 = syncclient.recv()
    print 'ready'

    # Process messages from receiver and controller
    poller = zmq.Poller()
    poller.register(receiver, zmq.POLLIN)
    poller.register(controller, zmq.POLLIN)

    parser = ArgumentParser()
    parser.add_argument('-r', '--remote_stub', action='store_true', help='remote stub')
    args = parser.parse_args(sys.argv[1:])
    remote_stub = args.remote_stub

    fill_field_funcs = []
    def fill_sentiment(item):
        sentiment = triple_classifier(item)
        item[XAPIAN_EXTRA_FIELD] = sentiment
        return item
    fill_field_funcs.append(fill_sentiment)

    s = load_scws()
    def cut_text(item):
        text = item['text'].encode('utf-8')
        item['terms'] = cut(s, text, cx=False)
        item['topics'] = list(set(item['terms']))

        return item
    fill_field_funcs.append(cut_text)

    count = 0

    while 1:
        evts = poller.poll(XAPIAN_ZMQ_POLL_TIMEOUT)
        if evts:
            socks = dict(poller.poll(XAPIAN_ZMQ_POLL_TIMEOUT))
        else:
            socks = None

        if socks and socks.get(receiver) == zmq.POLLIN:
            item = receiver.recv_json()
            if fill_field_funcs:
                for func in fill_field_funcs:
                    item = func(item)

            # index
            xapian_indexer.add_or_update(item)

            count += 1
            if count % XAPIAN_FLUSH_DB_SIZE == 0:
                te = time.time()
                cost = te - ts
                ts = te
                print '[%s] [%s] totalxapian index: %s, %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), xapian_indexer.db_folder, count, cost, XAPIAN_FLUSH_DB_SIZE)

        elif socks and socks.get(controller) == zmq.POLLIN:
            signal = controller.recv()
            if signal[8:] == 'BEGIN': # data deliver begin
                print 'BEGIN'
                datestr = '%s_data/' % signal[:8]

                if not os.path.exists(XAPIAN_DATA_DIR + datestr):
                    try:
                        os.makedirs(XAPIAN_DATA_DIR + datestr)
                    except:
                        pass

                dbpath = datestr + '_' + XAPIAN_DB_PATH
                xapian_indexer = XapianIndex(dbpath, SCHEMA_VERSION, remote_stub)
                ts = time.time()
                tb = ts

            elif signal == "END":
                print 'end'
                break

            elif signal == 'KILL':
                print 'killed'

