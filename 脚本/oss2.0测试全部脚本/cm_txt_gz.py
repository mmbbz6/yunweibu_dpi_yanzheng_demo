# -*- coding: utf-8 -*-
# !/usr/bin/env python

#########################################################
#
# 中国联通DPI采集整合测试之流量准确性验证
#  written by
#  todo:
#
#########################################################

import argparse
import ConfigParser
import sys
import tarfile
import datetime
import gzip
try:
    import psyco
    psyco.full()
except ImportError:
    pass

__version__ = '0.1'

if sys.version_info > (2, 7, 99):
    print("请使用python2版本，兼容pypy")
    exit()


def get_parser():
    parser = argparse.ArgumentParser(description='流量准确性验证脚本')
    parser.add_argument('-m', '--msisdn', help='msisdn列表', default='msisdn.txt')
    parser.add_argument('-o', '--output', help='输出', default='output')
    parser.add_argument('-l', '--list', help='Gn和S1U filelists', default='filelist')
    parser.add_argument('-v', '--version', help='displays the current version')
    return parser


parser = get_parser()
args = vars(parser.parse_args())


def _readConfig(conf):
    cp = ConfigParser.SafeConfigParser()
    cp.read(conf)
    config = {}
    try:
        config['MSISDN'] = int(cp.get('Gn', 'MSISDN')) - 1
        config['FLOW'] = int(cp.get('Gn', 'FLOW')) - 1
        return config
    except:
        logger.warning('话单格式配置文件conf不完整！')
        exit()

config = _readConfig('cm_conf')

def _loadMsisdn():
    msisdn_set = set()
    with open(args['msisdn']) as f:
        for i in f:
            msisdn_set.add(i.strip())

    return msisdn_set

def run():
    starttime = datetime.datetime.now()
    msisdn_set = _loadMsisdn()
    flow_dict = {}
    with open(args['list']) as f:
        for eachtar in f:
            eachtar = eachtar.strip()
            #print 'processing:%s' % eachtar
            try:
                ff = gzip.open(eachtar, "rb") 
                
                for eachline in ff: 
			items = eachline.strip().split('|')
                        msisdn = items[config['MSISDN']]
                        #print msisdn
                        if msisdn in msisdn_set:
				#if msisdn in flow_di
                                                #flow_dict[msisdn] = flow
                                print eachline 
            except:
                   continue

    #with open(args['output'], 'w') as f:
        #for key, value in flow_dict.items():
            #f.write('%s,%s\n' % (key, value))



    endtime = datetime.datetime.now()
    duration = (endtime - starttime).seconds
    #print '总共耗时%s秒，开始时间：%s,结束时间：%s' % (str(duration), str(starttime), str(endtime))

def command_line_runner():
    if args['version']:
        print(__version__)
        return

    run()


if __name__ == '__main__':
    	#print "ppp"
	command_line_runner()
