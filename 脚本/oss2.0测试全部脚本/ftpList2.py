# coding=utf-8
#########################################################################
# File Name: reg_url.py
# Author: WangWeilong
# Company: Baidu
#########################################################################

import re
import sys
from ftplib import FTP
from socket import error as SocketError
import errno

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
        try:
		self.filelist = self.ftp.nlst()
	except SocketError as e:
                if e.errno != errno.ECONNRESET:
                        raise
                pass

    def matchnames(self, regpattern):
        pattern = re.compile(regpattern)
        matchedfiles = []
        for file in self.filelist:
            match = pattern.search(file)
            if match:
                matchedfiles.append(match.string)
        return matchedfiles

    def downloadList(self, filename):
        with open(filename, 'w') as f:
            for file in self.filelist:
                f.write('%s\n' % file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'ftpList.py 20171117'
    # 解析ftpurl字符串
    else:
        #head = '10.162.160.203'
	head = '10.162.6.225'
        username = 'open_wy_pftp'
        passwd = 'WY_ftp_0614'
	#username = 'zbtest'
	#passwd = 'zbtest'
	
        #pathdir = '/files/open_wy_pftp/TEST/JS/BRD/LTE/' + sys.argv[1] + '/'
        #pathdir = '/files/open_wy_pftp/esbdata/SC/TEST/' + sys.argv[1] + '/'
        #pathdir = '/files/open_wy_pftp/SC/TEST/' + sys.argv[1] + '/'
	#pathdir = '/data1/esbdata/CQ/LTE/MOBILE/HUAWEI/OMC1/CXDR/' + sys.argv[1] + '/'

	#pathdir = '/files/open_wy_pftp/TEST/GZ/' + sys.argv[1] + '/'
	pathdir = '/files/open_wy_pftp/TEST/SXI/YONGDING/'  + sys.argv[1] + '/'
	#pathdir = '/files/open_wy_pftp/TEST/GZ/HH/'  + sys.argv[1] + '/'
	#pathdir = '/esbdata/JS/LTE/MOBILE/BROADTECH/OMC1/CXDR/'  + sys.argv[1] + '/'
	#pathdir = '/files/open_wy_pftp/TEST/HN/BROADTECH/' +  sys.argv[1] + '/'

	#pathdir = '/nmsdata/GZ/HH/TEST/'  + sys.argv[1] + '/'
	#pathdir = '/esbdata/JS/LTE/MOBILE/BROADTECH/OMC1/CXDR/'  + sys.argv[1] + '/'
        #pathdir = '/files/open_wy_pftp/TEST/CQ/LTE/MOBILE/HUAWEI/OMC1/DPI/' + sys.argv[1] + '/'
        #pathdir = '/files/open_wy_pftp/TEST/GZ/' + sys.argv[1] + '/'
        #head = '10.162.161.45'
        #username = 'sc_esb'
        #passwd = 'scftp!@328'
        #pathdir = '/esbdata/SC/TEST/' + sys.argv[1] + '/'
        #pathdir = '/files/' + sys.argv[1]
        #pathdir = '/esbdata/TEST/SC/' + sys.argv[1] + '/'
	#head = '10.162.161.34'
        #username = 'sc_esb'
        #passwd = 'scftp!@328'
	#pathdir = '/esbdata/SC/LTE/TEST/' + sys.argv[1] + '/'
    

        dhc_ftp = DHC_FTP(head, username, passwd)
        dhc_ftp.getftpfilelist(pathdir)

        filename = 'list2.' + sys.argv[1]
        dhc_ftp.downloadList(filename)
        
