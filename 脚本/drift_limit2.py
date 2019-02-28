# -*- coding: utf-8 -*-
# !/usr/bin/env python

#########################################################
#
# 中国联通DPI采集整合测试之6.2.5用户小区位置漂移率
#  written by Xiao v0.1 2017-09-23
#  modified 2017-11-22 限制抽取10000个用户，漂移匹配从距离、速度两者满足其一改成两者都满足
#  todo:词典的插入 和 遍历 字典纸中的排序  unzip write2file参数写成一个列表 转换字符生成默认format
#
#########################################################

import argparse
import ConfigParser
import logging.config
import sys
import operator
import tarfile
import datetime

from distance import Distance1

__version__ = '0.1'

if sys.version_info > (2, 7, 99):
    print("请使用python2版本，兼容pypy")
    exit()

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("example01")


def get_parser():
    parser = argparse.ArgumentParser(description='用户小区位置漂移率计算脚本')
    parser.add_argument('-l', '--list', help='抽样文件列表', default='./filelist')
    parser.add_argument('-o', '--output', help='输出文件', default='./locationDrift.csv')
    parser.add_argument('-d', '--distance', help='相邻时间距离告警阈值，单位米', default=10000)
    parser.add_argument('-s', '--speed', help='相邻时间速度告警阈值，单位米/秒', default=50)
    parser.add_argument('-v', '--version', help='displays the current version')
    return parser


parser = get_parser()
args = vars(parser.parse_args())


def _load_dictFormCELLINFO():  # 字典格式为  lac_cellid:(经度，纬度)
    cell_dict = {}
    cellEmpty = 0
    try:
        with open('cellinfo.txt', 'r') as f:
            for line in f:
                items = line.strip().split("\t")
                lac = items[0]
                cellid = items[1]
                if len(items) == 4:
                    try:
                        longitude = float(items[2])
                        latitude = float(items[3])
                    except:
                        logger.warning('小区经纬度填写不正确：%s,%s' % (lac, cellid))
                        continue
                    if (longitude < 73.66 or longitude > 135.05) or (latitude < 3.86 or latitude > 53.55):
                        logger.warning('该小区经纬度不在中国：%s,%s:%f,%f' % (lac, cellid, longitude, latitude))
                    else:
                        cell_dict[lac + "_" + cellid] = (longitude, latitude)
                        # return {line.strip().split(',')[0] + "_" + line.strip().split(',')[1]: (
                        # line.strip().split(',')[2], line.strip().split(',')[3]) for line in f}  # 除了手机号重复问题外，低效率不优雅

                else:
                    cellEmpty = cellEmpty + 1
                    # logger.warning('小区经纬度为空：%s,%s' % (lac, cellid))
        logger.warning('小区信息表中，经纬度为空的有%d行' % (cellEmpty))
        return cell_dict
    except:
        logger.warning('读取小区位置信息文件失败，默认./cellinfo.txt，格式为lac,cellid,经度,纬度')
        exit()


def _load_dictFormAIRPORT():  # 字典格式为  lac_cellid:场景
    airport_dict = {}
    try:
        with open('airport', 'r') as f:
            for line in f:
                items = line.strip().split("@")
                if len(items) == 4:
                    [lac, cellid, changjing1, changjing2] = items
                else:
                    continue
                airport_dict[lac + "_" + cellid] = (changjing1 + changjing2).decode('utf8').encode('gbk')
        return airport_dict
    except:
        logger.warning('读取机场高速高铁文件失败，默认airport，格式为lac@cellid@场景1@场景2')
        exit()


def testPrintDict(dic):
    for key, value in dic.items():
        print (key, ':', value)


# testPrintDict(cell_dict)

def _str2mirsecond(str):
    return datetime.datetime.strptime(str[:-1], '%Y-%m-%d %H:%M:%S.%f')


def _str2mirsecond_iucs(str):
    return datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S-%f')


def _str2mirsecond_iucs_sc(str):
    return datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S.%f')


def _write2file(*argss):
    with open(args['output'], 'a') as f:
        f.write('%s\n' % ','.join(str(s) for s in argss))


def _cgi2lacci(cgi):
    return (int(cgi[5:10]), int(cgi[10:]))


def _eci2lacci(eci):
    return (int(eci) / 256, int(eci) % 256)


def run():
    starttimer = datetime.datetime.now()
    cp = ConfigParser.SafeConfigParser()
    cp.read('drift_conf')
    customer_dict = {}
    customerNum = 1
    samplingNum = 0
    print 'load dict start'
    cell_dict = _load_dictFormCELLINFO()
    airport_dict = _load_dictFormAIRPORT()
    print 'load dict ok'
    # testPrintDict(cell_dict)
    _write2file(u'手机号码'.encode('gbk'), u'距离m'.encode('gbk'), u'速度m/s'.encode('gbk'), u'第一条记录开始时间'.encode('gbk'),
                u'lac_cellid'.encode('gbk'), u'基站场景'.encode('gbk'), u'纬度'.encode('gbk'), u'经度'.encode('gbk'),
                u'第二条记录开始时间'.encode('gbk'),
                u'lac_cellid'.encode('gbk'), u'基站场景'.encode('gbk'), u'纬度'.encode('gbk'), u'经度'.encode('gbk'),
                u'第一条记录来自于'.encode('gbk'),
                u'第二条记录来自于'.encode('gbk'))

    with open(args['list']) as f:
        for each in f:
            [filetype, eachtar] = each.strip().split('@')
            try:
                tar = tarfile.open(eachtar, "r:gz")
                logger.info('processing:%s' % eachtar)
                # print 'processing:%s' % eachtar
                for member in tar.getmembers():
                    ff = tar.extractfile(member)
                    for eachline in ff:
                        items = eachline.strip().split('|')

                        if filetype == 'IuCS':
                            rowLength = str(len(items))
                            fileclass = cp.get('IuCS', rowLength)
                            locationID = items[int(cp.get(fileclass, 'CGI')) - 1]
                            try:
                                (lac, cellid) = _cgi2lacci(locationID)
                            except:
                               # logger.warning('本条%s类型的记录没有小区标示信息(%s)：%s' % (filetype, rowLength, items))
                                continue
                            msisdn = int(cp.get(fileclass, 'MSISDN')) - 1
                            st = int(cp.get(fileclass, 'ST')) - 1
                            starttime = _str2mirsecond_iucs(items[st])
                            # starttime = _str2mirsecond_iucs_sc(items[st])
                        elif filetype == 'S1MME':
                            try:
                                fileclass = cp.get('S1MME', items[int(cp.get('S1MME', 'SDRTYPE')) - 1])
                            except:
                                continue
                            # fileclass = cp.get('S1MME', fileclass1)
                            locationID = items[int(cp.get(fileclass, 'ECI')) - 1]
                            if locationID == '':
                                continue
                            (lac, cellid) = _eci2lacci(locationID)
                            msisdn = int(cp.get(fileclass, 'MSISDN')) - 1
                            st = int(cp.get(fileclass, 'ST')) - 1
                            starttime = _str2mirsecond(items[st])
                        else:
                            try:
                                (lac, cellid) = (int(items[int(cp.get(filetype, 'LAC')) - 1]),
                                                 int(items[int(cp.get(filetype, 'CELLID')) - 1]))
                            except:
                                logger.warning('lac(%s) cellid(%s)有问题，文件名为%s#%s' % (
                                items[int(cp.get(filetype, 'LAC')) - 1], items[int(cp.get(filetype, 'CELLID')) - 1],
                                eachtar,eachline.strip()))
                                continue
                            locationID = str(lac) + '_' + str(cellid)
                            msisdn = int(cp.get(filetype, 'MSISDN')) - 1
                            st = int(cp.get(filetype, 'ST')) - 1
                            starttime = _str2mirsecond(items[st])
                            # 用户号码：(开始时间, lac_cellid, (经度，纬度))
                        cukey = items[msisdn]
                        if cukey != '':
                            lac_cellid = str(lac) + '_' + str(cellid)
                            try:
                                cuvalue = (starttime, lac_cellid, cell_dict[lac_cellid], eachtar)
                            except:
                                pass
                                # logger.warning("文件类型为%s的%s：该小区在cellinfo中找不到，对应的标识%s" % (filetype, lac_cellid, locationID))
                                # continue
                                cuvalue = (starttime, lac_cellid, 'XXX', eachtar)


                            if not customer_dict.has_key(cukey):
                                if customerNum < 10000:
                                    customer_dict[cukey] = [cuvalue]
                                    customerNum = customerNum + 1
                                    samplingNum = samplingNum + 1
                                else:
                                    continue
                            else:
                                customer_dict[cukey].append(cuvalue)
                                samplingNum = samplingNum + 1
            except:
                logger.warning('压缩文件解压错误:%s' % eachtar)

                #
    print "load file ok"

    # 对每个用户按时间进行排序,计算距离和速度
    for i in customer_dict.keys():
        newlist = sorted(customer_dict[i], key=operator.itemgetter(0))
        # print '%s sort ok' % i
        customer_dict[i] = newlist
        for j in xrange(len(newlist) - 1):
            if newlist[j][2] == 'XXX' or newlist[j + 1][2] == 'XXX':
                continue
            customer = i
            st1 = newlist[j][0]
            st2 = newlist[j + 1][0]
            long1 = newlist[j][2][1]
            lan1 = newlist[j][2][0]
            long2 = newlist[j + 1][2][1]
            lan2 = newlist[j + 1][2][0]
            lac_cellid1 = newlist[j][1]
            lac_cellid2 = newlist[j + 1][1]
            file1 = newlist[j][3]
            file2 = newlist[j + 1][3]

            if long1 == long2 or lan1 == lan2:
                continue

            try:
                distance = Distance1(float(long1), float(lan1), float(long2), float(lan2))
            except:
                print long1, lan1, long2, lan2

            if st1 == st2:
                _write2file(customer, distance, u'瞬时漂移'.encode('gbk'), st1, lac_cellid1,
                            airport_dict.get(lac_cellid1, u'普通场景'.encode('gbk')), long1, lan1, st2, lac_cellid2,
                            airport_dict.get(lac_cellid2, u'普通场景'.encode('gbk')),
                            long2, lan2, file1, file2)
                continue

            # 这里得解析时间然后再算时间差speed = _speed(distance, newlist[j][0], newlist[j+1][0])
            duration = float((st2 - st1).total_seconds())
            speed = distance / duration

            #if (distance > args['distance'] or speed > args['speed']):
            if (distance > args['distance'] and speed > args['speed']):
                _write2file(customer, distance, speed, st1, lac_cellid1,
                            airport_dict.get(lac_cellid1, u'普通场景'.encode('gbk')), long1, lan1, st2, lac_cellid2,
                            airport_dict.get(lac_cellid2, u'普通场景'.encode('gbk')), long2, lan2,
                            file1, file2)

    endtimer = datetime.datetime.now()
    duration = (endtimer - starttimer).seconds
    logger.info('总共耗时%s秒，开始时间：%s,结束时间：%s,一万个用户总记录数：%s' % (str(duration), str(starttimer), str(endtimer), str(samplingNum)))
    print '总共耗时%s秒，开始时间：%s,结束时间：%s,一万个用户总记录数：%s' % (str(duration), str(starttimer), str(endtimer), str(samplingNum))


def command_line_runner():
    if args['version']:
        print(__version__)
        return

    run()


if __name__ == '__main__':
    command_line_runner()

