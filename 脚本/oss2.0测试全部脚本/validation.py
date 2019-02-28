# -*- coding: utf-8 -*-
# !/usr/bin/env python

#########################################################
#
# 中国联通DPI采集整合测试之6.1.2 XDR话单规范性
#  written by Xiao v0.1 2017-10-10
#  todo: 格式化输出都改为format
#
#########################################################

import argparse
import ConfigParser
import logging.config
import sys
import re

__version__ = '0.1'

if sys.version_info > (2, 7, 99):
    print("请使用python2版本，兼容pypy")
    exit()

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("example01")


def get_parser():
    parser = argparse.ArgumentParser(description='XDR话单规范性检测脚本，部分字段使用正则表达式匹配')
    parser.add_argument('-f', '--file', help='通用话单文件列表', default='allType.sampling')
    parser.add_argument('-o', '--output', help='输出文件', default='XDR-Validation-Results.txt')
    parser.add_argument('-v', '--version', help='displays the current version')
    return parser


parser = get_parser()
args = vars(parser.parse_args())


def _write2file(*argss):
    with open(args['output'], 'a') as f:
        f.write('%s\n' % ','.join((str(s)) for s in argss))


def run():
    cp = ConfigParser.SafeConfigParser()
    cp.read('validation_conf')
    endwith = re.compile('.*\r\n')
    with open(args['file'], 'rb') as f:
        row = 0
        for eachline in f:
            row = row + 1
            if not endwith.match(eachline):
                logger.warn('第%d行没有以正确的回车换行符\\r\\n结尾:%s' % (row, eachline.strip()))
                _write2file('第%d行没有以正确的回车换行符\\r\\n结尾:%s' % (row, eachline.strip()))

            if len(eachline.strip().split('@')) != 2:
                continue
            [filetype, item] = eachline.strip().split('@')
            items = item.split('|')

            #liaoningIucs = re.compile('.*IuCS-.*')
            #if liaoningIucs.match(filetype):
            #    continue

            if filetype == 'IuCS' or filetype == 'IuPS' or filetype == 'Gb':
                fileclass = cp.get(filetype, items[0])
                filetype = fileclass

            for option in cp.options(filetype):
                [location, retype] = cp.get(filetype, option).split('@')
                if location == '0':
                    if retype != 'X':
                        if (len(items) - 1) != int(retype):
                            logger.warn('第%d行字段个数有问题,规范为%s个字段,本行为%d个字段：%s' % (row, retype, (len(items) - 1), eachline.strip()))
                            _write2file('第%d行字段个数有问题,规范为%s个字段,本行为%d个字段：%s' % (row, retype, (len(items) - 1), eachline.strip()))
                else:
                    field = items[int(location)]
                    if not re.match(retype, field):
                        logger.warn('第%d行第%s个字段"%s"格式有问题：%s' % (row, location, option, field))
                        _write2file('第%d行第%s个字段"%s"格式有问题：%s' % (row, location, option, field))


def command_line_runner():
    if args['version']:
        print(__version__)
        return

    run()


if __name__ == '__main__':
    command_line_runner()
