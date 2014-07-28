# -*- coding:utf-8 -*-

import sys
import time
import datetime

sys.path.append('../xapian_case')
from xapian_case.xapian_backend import XapianSearch
from xapian_case.utils import top_keywords, not_low_freq_keywords, gen_mset_iter

# 默认schema_version为2
s = XapianSearch(path='/home/ubuntu3/huxiaoqian/case/20140724/20140724/', name='master_timeline_weibo',schema_version='5')
#uesr
'''
count, get_results = s.search(query={'user': 1811093512}, fields=['text', 'timestamp', 'user', 'terms', '_id'])
print 'query1:'
if count!=0:
    for r in get_results():
        print "** " * 10
        print r['_id']
        print r['user']
        print r['text']
        print r['timestamp']
        print r['terms']

    print 'hits: %s' % count
else:
    print 'no results'
'''
get_results = s.iter_all_docs(fields=['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count'])
for r in get_results:
    print "** " * 10
    print r
'''  
    print r['terms'] 
#retweeted_mid
count, get_results =  s.search(query={'retweeted_mid': 3617750318549590}, fields=['text', 'timestamp', 'user', 'terms', '_id'])
print 'query2:'
if count!=0:
    for r in get_results():
        print "** " * 10
        print r['_id']
        print r['user']
        print r['text']
        print r['timestamp']
        print r['terms']

    print 'hits: %s' % count
else:
    print 'no results'

#message_type
count, get_results =  s.search(query={'message_type': 1}, fields=['text', 'timestamp', 'user', 'terms', '_id'])
print 'query3:'
if count!=0:
    for r in get_results():
        print "** " * 10
        print r['_id']
        print r['user']
        print r['text']
        print r['timestamp']
        print r['terms']

    print 'hits: %s' % count
else:
    print 'no results'

#sentiment
count, get_results =  s.search(query={'sentiment': 1}, fields=['text', 'timestamp', 'user', 'terms', '_id'])
print 'query8:'
if count!=0:
    for r in get_results():
        print "** " * 10
        print r['_id']
        print r['user']
        print r['text']
        print r['timestamp']
        print r['terms']

    print 'hits: %s' % count
else:
    print 'no results'


#_id
r =  s.search_by_id(id_=3617761840458250,fields=['text', 'timestamp', 'user', 'terms', '_id'])
print 'query4:'
print r['_id']
print r['user']
print r['terms']

d=r['terms']
for k in d:
    print k.encode['gbk']


#根据时间范围查询
timearray=time.strptime('2013-09-01 08:30:00','%Y-%m-%d %H:%M:%S')
begin_ts1 = int(time.mktime(timearray))
print 'query5:'
query_dict = {
    'timestamp': {'$gt': begin_ts1, '$lt': begin_ts1 + 3600},
}
count, get_results = s.search(query=query_dict , fields=['text', 'timestamp', 'user', 'terms', '_id'])
if count!=0:
   for r in get_results():
        print "** " * 10
        print r['_id']
        print r['user']
        print r['text']
        print r['timestamp']
        print r['terms']
   print 'hits: %s' % count
else:
    print 'no results'


#根据reposts_count范围查询
print 'query6:'
query_dict={
   'reposts_count': {'$gt': 50, '$lt': 100},
}
count, get_results = s.search(query=query_dict , fields=['text', 'timestamp', 'user', 'terms', '_id'])
if count!=0:
   for r in get_results():
        print "** " * 10
        print r['_id']
        print r['user']
        print r['text']
        print r['timestamp']
        print r['terms']
   print 'hits: %s' % count
else:
    print 'no results'
   
#根据comments_count
print 'query7:'
query_dict={
   'comments_count': {'$gt': 50, '$lt': 100},
}
count, get_results = s.search(query=query_dict , fields=['text', 'timestamp', 'user', 'terms', '_id'])
if count!=0:
   for r in get_results():
        print "** " * 10
        print r['_id']
        print r['user']
        print r['text']
        print r['timestamp']
        print r['terms']
   print 'hits: %s' % count
else:
    print 'no results'
'''
