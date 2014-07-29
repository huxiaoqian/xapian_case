##xapian_case配置

###1. 结构说明

三台服务器：
219.224.135.49   原始csv文件存储机器以及redis服务器
219.224.135.48   数据缓冲机器
219.224.135.47   建立索引机器

xapian_case主体部分主要由xapian_case，zmq_index，zmq_topic_workspace三个文件夹组成。
zmq_topic_workspace主要完成49向48分发数据以及48接收数据的功能。
zmq_index主要完成48向47分发数据以及47接收数据的功能。
xapian_case主要完成47建立索引的功能。

###2. 配置流程

2.1 原始数据分发
1）原始数据时间分片
一天的csv文件（一天一个）按照时间段分为96个csv文件。即通过运行/tool/csv_cut.py进行数据分片，需要对数据存放的文件夹地址配置：
```
    csv_dir_path = '/ubuntu5/huxiaoqian/xapian_case/data/weibo_201309/csv/'  # 原始数据文件夹
    now_datestr = sys.argv[1]
    source_path = csv_dir_path + '%s/' % now_datestr
    dest_path = csv_dir_path + '%s_cut/' % now_datestr                       # 分片数据文件夹
    source_files = os.listdir(source_path)
```
2）数据分发
/xapian_case/zmq_topic_workspace/config.py 文件进行如下配置：
```
    XAPIAN_ZMQ_VENT_HOST = '192.168.1.5'    # 原始csv文件存储机器的ip
    CSV_INPUT_FILEPATH = '/ubuntu5/huxiaoqian/xapian_case/data/weibo_201309/csv/20130918_cut/   #对应上面的分片数据文件夹
    VENT_REDIS_HOST = '192.168.1.5'         # redis服务器的地址
```

2.2 数据缓冲区接收及分发

2.3 索引数据接收


###3. 注意事项
