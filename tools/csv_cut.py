# -*- coding: UTF-8 -*-

import os
import time
import urllib
import json
import sys
from xapian_case.utils import get_now_db_no

ORIGIN_KEYS = ['user', 'retweeted_uid', '_id', 'retweeted_mid', 'timestamp',
               'input_time', 'geo', 'province', 'city', 'message_type', 'user_fansnum',
               'user_friendsnum', 'comments_count', 'reposts_count',
               'retweeted_comments_count', 'retweeted_reposts_count', 'text', 'is_long',
               'bmiddle_pic', 'pic_content', 'audio_url', 'audio_content', 'video_url',
               'video_content', 'sp_type']
RESP_ITER_KEYS = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text',
                  'timestamp', 'reposts_count', 'source', 'bmiddle_pic',
                  'geo', 'attitudes_count', 'comments_count', 'message_type']
CONVERT_TO_INT_KEYS = ['_id', 'user', 'retweeted_uid', 'retweeted_mid',
                       'reposts_count', 'comments_count', 'timestamp', 'message_type']
ABSENT_KEYS = ['attitudes_count', 'source']
IP_TO_GEO_KEY = 'geo'
MID_STARTS_WITH_C = '_id' # weibo mid starts with 'c_'
SP_TYPE_KEYS = '1' # 1??????

# IP address manipulation functions
def numToDottedQuad(n):
    "convert long int to dotted quad string"

    d = 256 * 256 * 256
    q = []
    while d > 0:
        m, n = divmod(n, d)
        q.append(str(m))
        d = d / 256

    return '.'.join(q)

def ip2geo(ip_addr):
    # ip_addr: '236112240'
    DottedIpAddr = numToDottedQuad(int(ip_addr))
    return DottedIpAddr


def WeiboItem(itemList):
    weibo = dict()

    for key in RESP_ITER_KEYS:

        value = None

        if key not in ABSENT_KEYS:
            value = itemList[ORIGIN_KEYS.index(key)]

            if key == IP_TO_GEO_KEY:
                value = ip2geo(value)

            elif key == MID_STARTS_WITH_C:
                if value[:2] == 'c_':
                    value = int(value[2:])
                else:
                    value = int(value)

            elif key in CONVERT_TO_INT_KEYS:
                value = int(value) if value != '' else 0

        if value is not None:
            weibo[key] = value

    return weibo


class UnkownParseError(Exception):
    pass


def itemLine2Dict(line):
    line = line.decode("utf8", "ignore")
    itemlist = line.strip().split(',')
    if itemlist[-1] == SP_TYPE_KEYS:
        if len(itemlist) != 25:
            try:
                tp = line.strip().split('"')
                if len(tp) != 3:
                    raise UnkownParseError()
                field_0_15, field_16, field_17_24 = tp
                field_0_15 = field_0_15[:-1].split(',')
                field_17_24 = field_17_24[1:].split(',')
                field_0_15.extend([field_16])
                field_0_15.extend([field_17_24])
                itemlist = field_0_15
                if len(itemlist) != 25:
                    raise UnkownParseError()
            except UnkownParseError:
                return None
    else:
        return None

    try:
        itemdict = WeiboItem(itemlist)
    except:
        itemdict = None

    return itemdict


def get_now_csv_no(ts):
    local_ts = int(ts) - time.timezone
    return int(local_ts) % (24 * 60 * 60) / (15 * 60) + 1

def main():
    begin_datestr = sys.argv[1] # 统计的开始日期
    end_datestr = sys.argv[2] # 统计的截止日期
    # need to create directory csv_dir_path + './%s_cut/' % now_datestr
    csv_dir_path = '/home/mirage/dev/original_data/csv/'
    csv_cut_path = '/home/mirage/dev/cut_data/csv/'

    csv_files = os.listdir(csv_dir_path)
    for csv_file in csv_files:
        now_datestr = os.path.basename(csv_file)

        if (now_datestr >= begin_datestr and now_datestr <= end_datestr):
            source_path = csv_dir_path + '%s/' % now_datestr
            dest_path = csv_cut_path + '%s_cut/' % now_datestr
            print now_datestr,'chosen'
            if not(os.path.exists(dest_path)):
                os.makedirs(dest_path)
                print now_datestr,'makedir'


                source_files = os.listdir(source_path)
                count = 0
                ts = te = time.time()
                for f in source_files:
                    print 'f', f
                    f = open(source_path + f, 'r')
                    try:
                        for line in f:
                            itemdict = itemLine2Dict(line)
                            if itemdict:
                                item_timestamp = itemdict['timestamp']
                                csv_no = get_now_csv_no(item_timestamp)

                                fw = open(dest_path + str(csv_no) + '.csv', 'a')
                                fw.write(line + '\n')
                                fw.close()

                            if count % 10000 == 0:
                                te = time.time()
                                print count, '%s sec' % (te - ts)
                                ts = te
                            count += 1
                    except:
                        pass
                    f.close()


if __name__ == '__main__':
    main()
