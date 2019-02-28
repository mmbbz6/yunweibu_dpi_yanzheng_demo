#!/bin/bash
while getopts 'd:' OPT; do
    case $OPT in
        d)
            DIR="$OPTARG";;
        ?)
            echo "Usage: `basename $0` -d "搜索目录""
    esac
done

optnum=$(($OPTIND - 1))

shift $(($OPTIND - 1))

if [ $optnum -ne 2 ];then
        echo "Usage: `basename $0` -d "搜索目录"
                统计某个目录下不同类型文件的个数"
        exit
fi

output=`echo ${DIR##*/}`

rm -rf $output.log
echo "TYPE",$output > $output.log
ls $DIR|awk 'BEGIN{FS="_";OFS=","} {array[$10]++} END{for(i in array) print i,array[i]}'|sort|tee -a $output.log
echo "successed! see $output.log"