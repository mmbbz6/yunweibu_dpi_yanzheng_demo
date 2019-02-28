#!/bin/bash
#提取某个目录下某种类型文件连续若干小时的列表
while getopts 'd:t:s:c:' OPT; do
    case $OPT in
        d)
            DIR="$OPTARG";;
        t)
            TYPE="$OPTARG";;
        s)
            HOUR="$OPTARG";;
        c)
            DURATION="$OPTARG";;
        ?)
            echo "Usage: `basename $0` -d "搜索目录" -t "搜索文件类型" -s "抽样时间,例如20170812 16" -c "前后时间间隔，小时为单位""
    esac
done

optnum=$(($OPTIND - 1))

shift $(($OPTIND - 1))

if [ $optnum -ne 8 ];then
        echo "Usage: `basename $0` -d "搜索目录" -t "搜索文件类型" -s "抽样时间,例如20170812 16" -c "前后时间间隔，小时为单位"
               		提取某个目录下某种类型文件连续若干小时的列表，输出文件列表"
        exit
fi

starttime=`date -d "$HOUR -$DURATION hour" +"%Y%m%d%H"`
endtime=`date -d "$HOUR $DURATION hour" +"%Y%m%d%H"`

rm -rf filelist
ls $DIR|awk -v t=$TYPE -v st=$starttime -v et=$endtime -v dir=$DIR 'BEGIN{FS="_"} {split($10,a,"-"); if (a[1]==t && substr($9,0,10)>=st && substr($9,0,10)<=et) {printf "%s@%s%s\n",t,dir,$0}}'>>filelist
echo "successed! see filelist"
