#xapian_case配置

##1. 结构说明

三台服务器：
219.224.135.49   原始csv文件存储机器以及redis服务器
219.224.135.48   数据缓冲机器
219.224.135.47   建立索引机器

xapian_case主体部分主要由xapian_case，zmq_index，zmq_topic_workspace三个文件夹组成。
zmq_topic_workspace主要完成49向48分发数据以及48接收数据的功能。
zmq_index主要完成48向47分发数据以及47接收数据的功能。
xapian_case主要完成47建立索引的功能。

##2. 配置流程

2.1 原始数据分发

2.2 数据缓冲区接收及分发

2.3 索引数据接收


##3. 注意事项
