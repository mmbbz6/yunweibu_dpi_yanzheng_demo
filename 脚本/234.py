# -*- coding: utf-8 -*-
# !/usr/bin/env python

#########################################################
#
# 中国联通DPI采集整合测试之5.1.1 2/3G采集和4G采集整合验证
#  written by Xiao v0.1 2017-09-19
#  todo:时间窗口、现在两条记录的匹配方法是两条记录的时间段重叠
#
#########################################################

import argparse
import ConfigParser
import logging.config
import sys
import tarfile
import datetime

__version__ = '0.1'

if sys.version_info > (2, 7, 99):
    print("请使用python2版本，兼容pypy")
    exit()

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("example01")


def get_parser():
    parser = argparse.ArgumentParser(description='2/3G与4G采集整合验证脚本')
    parser.add_argument('-d', '--dir', help='选择抽样的csfb文件', default='sampling.txt')
    parser.add_argument('-o', '--output', help='输出文件位置', default='matched.txt')
    parser.add_argument('-n', '--output2', help='输出文件位置', default='notmatched.txt')
    parser.add_argument('-l', '--list', help='A/InCS filelists', default='IuCS.list')
    parser.add_argument('-v', '--version', help='displays the current version')
    return parser


parser = get_parser()
args = vars(parser.parse_args())


def _readConfig(conf):
    cp = ConfigParser.SafeConfigParser()
    cp.read(conf)
    config = {}
    try:
        config['CSFB_MSISDN'] = int(cp.get('CSFB', 'MSISDN')) - 1
        config['CSFB_ST'] = int(cp.get('CSFB', 'ST')) - 1
        config['CSFB_ET'] = int(cp.get('CSFB', 'ET')) - 1
        config['CSFB_LAI'] = int(cp.get('CSFB', 'LAI')) - 1
        config['CSFB_FAIL'] = int(cp.get('CSFB', 'FAIL')) - 1
        config['IUCS_VOICE_LENGTH'] = int(cp.get('IUCS', 'VOICE_LENGTH'))
        config['IUCS_VOICE_MSISDN'] = int(cp.get('IUCS', 'VOICE_MSISDN')) - 1
        config['IUCS_VOICE_ST'] = int(cp.get('IUCS', 'VOICE_ST')) - 1
        config['IUCS_VOICE_ET'] = int(cp.get('IUCS', 'VOICE_ET')) - 1
        config['IUCS_VOICE_LAI'] = int(cp.get('IUCS', 'VOICE_LAI')) - 1
        config['IUCS_VOICE_FAIL'] = int(cp.get('IUCS', 'VOICE_FAIL')) - 1
        config['IUCS_SMS_LENGTH'] = int(cp.get('IUCS', 'SMS_LENGTH'))
        config['IUCS_SMS_MSISDN'] = int(cp.get('IUCS', 'SMS_MSISDN')) - 1
        config['IUCS_SMS_ST'] = int(cp.get('IUCS', 'SMS_ST')) - 1
        config['IUCS_SMS_ET'] = int(cp.get('IUCS', 'SMS_ET')) - 1
        config['IUCS_SMS_LAI'] = int(cp.get('IUCS', 'SMS_LAI')) - 1
        config['IUCS_SMS_FAIL'] = int(cp.get('IUCS', 'SMS_FAIL')) - 1
        config['IUCS_LOCATION_LENGTH'] = int(cp.get('IUCS', 'LOCATION_LENGTH'))
        config['IUCS_LOCATION_MSISDN'] = int(cp.get('IUCS', 'LOCATION_MSISDN')) - 1
        config['IUCS_LOCATION_ST'] = int(cp.get('IUCS', 'LOCATION_ST')) - 1
        config['IUCS_LOCATION_ET'] = int(cp.get('IUCS', 'LOCATION_ET')) - 1
        config['IUCS_LOCATION_LAI'] = int(cp.get('IUCS', 'LOCATION_LAI')) - 1
        config['IUCS_LOCATION_FAIL'] = int(cp.get('IUCS', 'LOCATION_FAIL')) - 1
        config['IUCS_SHIFT_LENGTH'] = int(cp.get('IUCS', 'SHIFT_LENGTH'))
        config['IUCS_SHIFT_MSISDN'] = int(cp.get('IUCS', 'SHIFT_MSISDN')) - 1
        config['IUCS_SHIFT_ST'] = int(cp.get('IUCS', 'SHIFT_ST')) - 1
        config['IUCS_SHIFT_ET'] = int(cp.get('IUCS', 'SHIFT_ET')) - 1
        config['IUCS_SHIFT_LAI'] = int(cp.get('IUCS', 'SHIFT_LAI')) - 1
        config['IUCS_SHIFT_FAIL'] = int(cp.get('IUCS', 'SHIFT_FAIL')) - 1
        config['IUCS_CALL_LENGTH'] = int(cp.get('IUCS', 'CALL_LENGTH'))
        config['IUCS_CALL_MSISDN'] = int(cp.get('IUCS', 'CALL_MSISDN')) - 1
        config['IUCS_CALL_ST'] = int(cp.get('IUCS', 'CALL_ST')) - 1
        config['IUCS_CALL_ET'] = int(cp.get('IUCS', 'CALL_ET')) - 1
        config['IUCS_CALL_LAI'] = int(cp.get('IUCS', 'CALL_LAI')) - 1
        config['IUCS_CALL_FAIL'] = int(cp.get('IUCS', 'CALL_FAIL')) - 1
        return config
    except:
        logger.warning('话单格式配置文件conf不完整！')
        exit()


config = _readConfig('conf')


def _str2mirsecond(str):
    return datetime.datetime.strptime(str[:-1], '%Y-%m-%d %H:%M:%S.%f')


def _str2mirsecond_iucs(str):
    return datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S-%f')


def _inDuration(duration1, duration2):
    # return 1 if (duration2[0] > duration1[0] and duration2[0] < duration1[1]) or (duration2[1] > duration1[0] and duration2[1] < duration1[1]) or (duration2[0] < duration1[0] and duration2[1] > duration1[1]) else 0
    return 0 if (duration2[0] > duration1[1]) or (duration2[1] < duration1[0]) else 1


# msisdn:st|et|lai|fail
def _load_dictFormCSFB(filepath, msisdn, st, et, lai, fail):
    CSFB_dict = {}
    try:
        with open(filepath) as f:
            for line in f:
                items = line.strip().split('|')
                MSISDN = items[msisdn]
                ST = items[st]
                ET = items[et]
                LAI = items[lai]
                FAIL = items[fail]
                if MSISDN == '' or ST == '' or ET == '':
                    logger.warning('导入CDFB字典：msisdn:%s,starttime:%s,endtime:%s有空的' % (MSISDN, ST, ET))
                    continue
                else:
                    if MSISDN in CSFB_dict:
                        logger.warning('导入CDFB字典：msisdn:%s重复' % (MSISDN))
                    else:
                        CSFB_dict[MSISDN] = [ST, ET, LAI, FAIL, 0]

        return CSFB_dict
        # return {line.strip().split('|')[msisdn]:[line.strip().split('|')[st],line.strip().split('|')[et],line.strip().split('|')[lac],line.strip().split('|')[cellid],line.strip().split('|')[fail]] for line in f} #除了手机号重复问题外，低效率不优雅
    except:
        logger.warning('读取抽样文件失败，默认samping.txt，使用-d 参数')
        exit()


def testPrintDict(dic):
    for key, value in dic.items():
        print (key, ':', value)


CSFB_sampling_dict = _load_dictFormCSFB(args['dir'], config['CSFB_MSISDN'], config['CSFB_ST'], config['CSFB_ET'],
                                        config['CSFB_LAI'], config['CSFB_FAIL'])

#testPrintDict(CSFB_sampling_dict)


def _write2file(csfb, iucs, msisdn, st, et, lai, fail):
    with open(args['output'], 'w') as f:
        # f.write('%s|%s\n' % (','.join(csfb), ','.join(iucs)))  #把IUCS的字段全部写入
        # f.write('%s\n' % (','.join(csfb + iucs))  #把IUCS的字段全部写入
        # f.write('%s\n' % '|'.join(csfb) + '|' +  ','.join([iucs[msisdn], iucs[st], iucs[et], iucs[lac], iucs[cellid], iucs[fail]]))
        f.write('%s\n' % ','.join(csfb + [iucs[msisdn], iucs[st], iucs[et], iucs[lai], iucs[fail]]))

def _is_matched(row, msisdn, st, et, lai, fail, filename, rownum, type):
    global CSFB_sampling_dict
    if row[msisdn] == '' or row[st] == '' or row[et] == '':
        pass
        #logger.warning('类型%s的文件%s第%s行字段有空：msisdn:%s,starttime:%s,endtime:%s.详细信息是%s' % (type, filename, rownum, row[msisdn], row[st], row[et], str(row)))
    else:
        if row[msisdn] in CSFB_sampling_dict:
            try:
                d11 = _str2mirsecond(CSFB_sampling_dict[row[msisdn]][0])
                d12 = _str2mirsecond(CSFB_sampling_dict[row[msisdn]][1])
                d21 = _str2mirsecond_iucs(row[st])
                d22 = _str2mirsecond_iucs(row[et])
                #d21 = _str2mirsecond_(row[st])
                #d22 = _str2mirsecond(row[et])
                if _inDuration([d11, d12], [d21, d22]):
                    _write2file([row[msisdn]] + CSFB_sampling_dict[row[msisdn]][:-1], row, msisdn, st, et, lai, fail)
                    CSFB_sampling_dict[row[msisdn]][4] = CSFB_sampling_dict[row[msisdn]][4] + 1
                    # logger.info('%s matched' % row[msisdn])
                else:
                    # logger.info('%s not matched' % row[msisdn])
                    pass
            except:
                logger.error('类型%s的文件%s第%s行时间格式有问题：msisdn:%s,starttime:%s,endtime:%s.详细信息是%s' % (type, filename, rownum, row[msisdn], row[st], row[et], str(row)))
                pass
        else:
            # logger.info('%s not in dict' % row[msisdn])
            pass


def run():
    starttime = datetime.datetime.now()
    with open(args['list']) as f:
        for eachtar in f:
            eachtar = eachtar.strip()
            try:
                tar = tarfile.open(eachtar, "r:gz")
                logger.info('processing:%s' % eachtar)
                for member in tar.getmembers():
                    ff = tar.extractfile(member)
                    rownum = 0
                    for eachline in ff:
                        rownum = rownum + 1
                        items = eachline.strip().split('|')
                        num = len(items)
                        if num == config['IUCS_VOICE_LENGTH']:
                            match = _is_matched(items, config['IUCS_VOICE_MSISDN'], config['IUCS_VOICE_ST'],
                                                config['IUCS_VOICE_ET'], config['IUCS_VOICE_LAI'],
                                                config['IUCS_VOICE_FAIL'], eachtar, rownum, 'VOICE')
                        elif num == config['IUCS_SMS_LENGTH']:
                            match = _is_matched(items, config['IUCS_SMS_MSISDN'], config['IUCS_SMS_ST'],
                                                config['IUCS_SMS_ET'], config['IUCS_SMS_LAI'], config['IUCS_SMS_FAIL'],
                                                eachtar, rownum, 'SMS')
                        elif num == config['IUCS_LOCATION_LENGTH']:
                            match = _is_matched(items, config['IUCS_LOCATION_MSISDN'], config['IUCS_LOCATION_ST'],
                                                config['IUCS_LOCATION_ET'], config['IUCS_LOCATION_LAI'],
                                                config['IUCS_LOCATION_FAIL'], eachtar, rownum, 'LOCATION')
                        elif num == config['IUCS_SHIFT_LENGTH']:
                            match = _is_matched(items, config['IUCS_SHIFT_MSISDN'], config['IUCS_SHIFT_ST'],
                                                config['IUCS_SHIFT_ET'], config['IUCS_SHIFT_LAI'],
                                                config['IUCS_SHIFT_FAIL'], eachtar, rownum, 'SHIFT')
                        elif num == config['IUCS_CALL_LENGTH']:
                            match = _is_matched(items, config['IUCS_CALL_MSISDN'], config['IUCS_CALL_ST'],
                                                config['IUCS_CALL_ET'], config['IUCS_CALL_LAI'],
                                                config['IUCS_CALL_FAIL'], eachtar, rownum, 'CALL')
                        else:
                            logger.warning('该行列数与规范不匹配：%s' % eachline.strip())
    
                tar.close()
            except:
                logger.warning('压缩文件解压错误:%s' % eachtar)

    with open(args['output2'], 'w') as f:
        for key, value in CSFB_sampling_dict.items():
            if value[4] == 0:
                f.write('CSFB中抽样的记录%s:%s未在IuCS文件中匹配到\n' % (key, str(value)))

    endtime = datetime.datetime.now()
    duration = (endtime - starttime).seconds
    logger.info('总共耗时%s秒，开始时间：%s,结束时间：%s' % (str(duration), str(starttime), str(endtime)))
    print '总共耗时%s秒，开始时间：%s,结束时间：%s' % (str(duration), str(starttime), str(endtime))


def command_line_runner():
    if args['version']:
        print(__version__)
        return

    run()


if __name__ == '__main__':
    command_line_runner()

