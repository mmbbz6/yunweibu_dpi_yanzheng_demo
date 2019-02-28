#!/bin/bash
while getopts 'l:' OPT; do
    case $OPT in
        l)
            LIST="$OPTARG";;
        ?)
            echo "Usage: `basename $0` -l"文件列表""
    esac
done

optnum=$(($OPTIND - 1))

shift $(($OPTIND - 1))

if [ $optnum -ne 2 ];then
        echo "Usage: `basename $0` -l "文件列表"
                统计文件列表下不同类型文件的个数"
        exit
fi

output=$LIST

rm -rf $output.log
echo "TYPE",$output > $output.log
cat $LIST|awk 'BEGIN{FS="_";OFS=","} {split($10,a,"-") array[a[1]]++} END{for(i in array) print i,array[i]}'|sort|tee -a $output.log
echo "successed! see $output.log"
