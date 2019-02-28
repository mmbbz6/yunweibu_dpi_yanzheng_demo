#!/bin/bash
#提取某个目录下Gn和S1U的文件列表
while getopts 'd:t:s:c:' OPT; do
    case $OPT in
        d)
            DIR="$OPTARG";;
        ?)
            echo "Usage: `basename $0` -d "搜索目录" "
    esac
done

optnum=$(($OPTIND - 1))

shift $(($OPTIND - 1))

if [ $optnum -ne 2 ];then
        echo "Usage: `basename $0` -d "搜索目录" 
                        提取某个目录下Gn S1-U，输出文件列表"
        exit
fi
rm -f GnS1U.list
ls $DIR|awk -v d=$DIR 'BEGIN{FS="_";OFS="/"} {if ($10=="Gn") {print d,$0}}' >>  GnS1U.list
ls $DIR|awk -v d=$DIR 'BEGIN{FS="_";OFS="/"} {if ($10=="S1U") {print d,$0}}' >>  GnS1U.list