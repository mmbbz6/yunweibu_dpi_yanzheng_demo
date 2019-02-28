# coding:utf-8
import os
import sys
import ftplib


class myFtp:
    ftp = ftplib.FTP()
    bIsDir = False
    path = ""

    def __init__(self, host, port='21'):
        self.ftp.set_debuglevel(2)  # 打开调试级别2，显示详细信息
        # self.ftp.set_pasv(0)    #0主动模式 1 #被动模式
        self.ftp.connect(host, port)

    def Login(self, user, passwd):
        self.ftp.login(user, passwd)
        print self.ftp.welcome

    def DownLoadFile(self, LocalFile, RemoteFile):
        file_handler = open(LocalFile, 'wb')
        self.ftp.retrbinary("RETR %s" % (RemoteFile), file_handler.write)
        file_handler.close()
        return True

    def DownLoadFileList(self, FileList, LocalDir, RemoteDir):
        with open(FileList) as f:
            for line in f:
                self.DownLoadFile(LocalDir + line.strip(), RemoteDir + line.strip())
        return True


    def UpLoadFile(self, LocalFile, RemoteFile):
        if os.path.isfile(LocalFile) == False:
            return False
        file_handler = open(LocalFile, "rb")
        self.ftp.storbinary('STOR %s' % RemoteFile, file_handler, 4096)
        file_handler.close()
        return True

    def UpLoadFileTree(self, LocalDir, RemoteDir):
        if os.path.isdir(LocalDir) == False:
            return False
        LocalNames = os.listdir(LocalDir)
        print RemoteDir
        self.ftp.cwd(RemoteDir)
        for Local in LocalNames:
            src = os.path.join(LocalDir, Local)
            if os.path.isdir(src):
                self.UpLoadFileTree(src, Local)
            else:
                self.UpLoadFile(src, Local)

        self.ftp.cwd("..")
        return

    def DownLoadFileTree(self, LocalDir, RemoteDir):
        if os.path.isdir(LocalDir) == False:
            os.makedirs(LocalDir)
        self.ftp.cwd(RemoteDir)
        RemoteNames = self.ftp.nlst()
        for file in RemoteNames:
            Local = os.path.join(LocalDir, file)
            if self.isDir(file):
                self.DownLoadFileTree(Local, file)
            else:
                self.DownLoadFile(Local, file)
        self.ftp.cwd("..")
        return

    def show(self, list):
        result = list.lower().split(" ")
        if self.path in result and "<dir>" in result:
            self.bIsDir = True

    def isDir(self, path):
        self.bIsDir = False
        self.path = path
        # this ues callback function ,that will change bIsDir value
        self.ftp.retrlines('LIST', self.show)
        return self.bIsDir

    def close(self):
        self.ftp.quit()



if __name__ == "__main__":
    if len(sys.argv) != 4:
        print 'usage:python ftpUtil.py list localdir remotedir(/files/open_wy_pftp/TEST/LN/20171125/)'
    else:
        ftp = myFtp('10.162.6.225')
        ftp.Login('open_wy_pftp', 'WY_ftp_0614')
        ftp.DownLoadFileList(sys.argv[1], sys.argv[2], sys.argv[3])
        # ftp.DownLoadFile('TEST.TXT', 'others\\runtime.log')#ok
        # ftp.UpLoadFile('runtime.log', 'others\\runtime.log')#ok
        # ftp.DownLoadFileTree('bcd', 'others\\abc')#ok
        # ftp.UpLoadFileTree('aaa',"others\\" )

        ftp.close()
        print "ok!"
