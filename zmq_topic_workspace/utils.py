# -*- coding: utf-8 -*-

class UnkownParseError(Exception):
    pass


def itemLine2Json(line):
    line = line.decode("utf8", "ignore")
    itemlist = line.strip().split(',')
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

    itemdict = {'weibo': itemlist}
    return itemdict


def json2csvrow(item):
    csvrow = None
    if item and type(item) is dict and 'weibo' in item:
        weibo_item = [i.encode('utf-8') for i in item['weibo']]
        csvrow = weibo_item

    return csvrow
    