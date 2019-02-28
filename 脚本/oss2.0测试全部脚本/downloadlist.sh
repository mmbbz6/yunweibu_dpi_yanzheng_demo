#!/bin/bash
while getopts 'l:d:' OPT; do
    case $OPT in
        l)
            LIST="$OPTARG";;
        d)
            DATE="$OPTARG";;
        ?)
            echo "Usage: `basename $0` -l"文件列表" -d 20171204"
    esac
done

optnum=$(($OPTIND - 1))

shift $(($OPTIND - 1))

if [ $optnum -ne 4 ];then
        echo "Usage: `basename $0` -l "文件列表"
                抽取需要下载的文件列表"
        exit
fi


rm -rf download.filelist download.list
echo '234整合文件'
cat $LIST|grep IuCS>>download.list
cat $LIST|grep CSFB>>download.list

echo '漂移文件'
cat $LIST|grep .*${DATE}20.*S1MME[-_].* >>download.list
cat $LIST|grep .*${DATE}20.*S1U[-_].* >>download.list
cat $LIST|grep .*${DATE}20.*Gn[-_].* >>download.list
cat $LIST|grep .*${DATE}21.*S1MME[-_].* >>download.list
cat $LIST|grep .*${DATE}21.*S1U[-_].* >>download.list
cat $LIST|grep .*${DATE}21.*Gn[-_].* >>download.list
cat $LIST|grep .*${DATE}22.*S1MME[-_].* >>download.list
cat $LIST|grep .*${DATE}22.*S1U[-_].* >>download.list
cat $LIST|grep .*${DATE}22.*Gn[-_].* >>download.list

echo '抽样文件'
for i in `cut -d '_' -f 10 $LIST|cut -d '-' -f 1|sort -u`
do
    echo $i
    cat $LIST|grep $i|shuf -n10>>download.list
done
cat download.list|sort -u>download.filelist
rm -f download.list

