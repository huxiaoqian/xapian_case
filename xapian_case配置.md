##xapian_case配置

###1. 结构说明

三台服务器：

219.224.135.49(192.168.1.5)   原始csv文件存储机器以及redis服务器

219.224.135.48(192.168.1.4)   数据缓冲机器

219.224.135.47(192.168.1.3)   建立索引机器

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
    CSV_INPUT_FILEPATH = '/ubuntu5/huxiaoqian/xapian_case/data/weibo_201309/csv/20130918_cut/'   #对应上面的分片数据文件夹
    VENT_REDIS_HOST = '192.168.1.5'         # redis服务器的地址
```
作如下操作：
```
    cd /home/ubuntu5/huxiaoqian/xapian_case/zmq_topic_workspace
    python xapian_zmq_vent_json.py
```

2.2 数据缓冲区接收及分发

1）数据接收（来自49）

/xapian_case/zmq_topic_workspace/config.py 文件对存储数据的地址进行配置：
```
    CSV_FLOW_PATH = '/home/ubuntu4/huxiaoqian/xapian_case/data/weibo_201309/csv/flow/'
```
在命令行执行如下操作接收49传来的数据：
```
    cd /home/ubuntu4/huxiaoqian/xapian_case/zmq_topic_workspace
    python xapian_zmq_write_csv.py
```

2）数据分发（发向47）

/xapian_case/zmq_index/consts.py 文件对数据分发向47做vent ip等如下配置：

```
    XAPIAN_ZMQ_VENT_HOST = '192.168.1.4'            #48向47分发数据时，48为vent_host
    VENT_REDIS_HOST = '192.168.1.5'                 #整个流程redis服务器始终为49
    CSV_FILEPATH = '/home/ubuntu4/huxiaoqian/xapian_case/data/weibo_201309/csv/flow/'  #对应上面csv文件存储地址
```
在命令行开启数据分发：
```
    cd /home/ubuntu4/huxiaoqian/xapian_case/zmq_index
    python xapian_zmq_vent.py
```

2.3 索引数据接收

/xapian_case/zmq_index/consts.py 文件对数据接收地址进行如下配置：
```
    XAPIAN_DATA_DIR = '/home/ubuntu3/huxiaoqian/xapian_case/data/weibo_201309/data/'
    XAPIAN_STUB_FILE_DIR= '/home/ubuntu3/huxiaoqian/xapian_case/data/weibo_201309/stub/'
```
在命令行开启索引构建：
```
    cd /home/ubuntu3/huxiaoqian/xapian_case/zmq_index
    python xapian_zmq_work.py
```

###3. 注意事项

3.1 redis服务器

1）redis服务器安装

```
    wget http://download.redis.io/releases/redis-2.8.13.tar.gz   #下载redis
    tar xzf redis-2.8.13.tar.gz                                  #解压
    cd redis-2.8.13
    make
    vim redis.conf
    #进入redis.conf文件后，将demonlize后面的no 改为yes
```

2）当构建索引过程中，因某些问题暂停。再一次开启索引的时候，注意将redis服务器内存中暂留的相关数据进行清空。
```
    src/redis_cli                           #进入redis客户端
    lrange 'global_vent_index:queue' 0 -1   #查看redis中的文件
    del 'global_vent_index:queue' 0 -1      #删除redis中所有的文件
```

3）当需要从redis推送某个csv文件时 进行如下操作：
```
    src/redis_cli                                 
    lpush 'global_vent_index:queue' csv文件名 #推送redis中某个csv文件
```







