#!/bin/bash
while getopts 'l:n:f:' OPT; do
    case $OPT in
        l)
            LIST="$OPTARG";;
        n)
            NUM="$OPTARG";;
		f)
			FIELD="$OPTARG";;
        ?)
            echo "Usage: `basename $0` -l "要搜索的文件列表文件"  -n "需要抽取多少个手机号码" -f "msisdn在第几个字段""
    esac
done

optnum=$(($OPTIND - 1))

shift $(($OPTIND - 1))

if [ $optnum -ne 6 ];then
        echo "Usage: `basename $0` -l "要搜索的文件列表文件"  -n "需要抽取多少个手机号码" -f "msisdn在第几个字段"
		在文件列表的文件中抽取若干个手机号,需要用-f参数指定msisdn在文件第几个字段 "
        exit
fi

rm -f msisdn.tmp msisdn.txt

for file in `cat $LIST` 
do
	zcat $file|cut -d "|" -f $FIELD >> msisdn.tmp
done

num=`cat msisdn.tmp|sort -u|wc -l`

if [ $num -lt $NUM ];then
	echo "文件中的msisdn数量$num少于需要抽样的手机号数量$NUM个，请增加文件列表里的文件数量"
	rm -f msisdn.tmp
	exit
else
	cat msisdn.tmp|sort -u|shuf -n$NUM >> msisdn.txt
fi
rm -f msisdn.tmp
echo "successed! see msisdn.txt"
