# coding=utf-8
#########################################################################
# File Name: reg_url.py
# Author: WangWeilong
# Company: Baidu
#########################################################################

import re
import sys
from ftplib import FTP


class DHC_FTP():
    def __init__(self, hostname, username="", passwd=""):
        self.hostname = hostname
        try:
            self.ftp = FTP(self.hostname)
        except:
            print "hostname error!"
            exit(-1)
        self.username = username
        self.passwd = passwd
        self.filelist = []
        self.reg_pattern = ""

    def getftpfilelist(self, path):
        self.ftp.login(self.username, self.passwd)
        self.ftp.cwd(path)
        self.filelist = self.ftp.nlst()

    def matchnames(self, regpattern):
        pattern = re.compile(regpattern)
        matchedfiles = []
        for file in self.filelist:
            match = pattern.search(file)
            if match:
                matchedfiles.append(match.string)
        return matchedfiles


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'ftpList.py 20171117'
    # 解析ftpurl字符串
    else:
        head = '10.162.6.225'
        username = 'open_wy_pftp'
        passwd = 'WY_ftp_0614'
        pathdir = '/files/open_wy_pftp/TEST/LN/' + sys.argv[1] + '/'
        #pathdir = '/files/' + sys.argv[1]
    

        dhc_ftp = DHC_FTP(head, username, passwd)
        dhc_ftp.getftpfilelist(pathdir)

    # 获取正则表达式
        regpattern = r'.*'

        matchedfiles = dhc_ftp.matchnames(regpattern)
        with open('list.' + sys.argv[1], 'w') as f:
            for files in matchedfiles:
                ftpname =  files
                f.write('%s\n' % ftpname)
