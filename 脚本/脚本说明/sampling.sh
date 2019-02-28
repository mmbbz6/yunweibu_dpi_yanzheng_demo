#!/bin/bash
#在某个目录下随机抽取某种类型的文件若干个，每个文件抽取若干条记录，输出记录
while getopts 'd:t:f:r:' OPT; do
    case $OPT in
        d)
            DIR="$OPTARG";;
        t)
            TYPE="$OPTARG";;
        f)
            FILENUM="$OPTARG";;
        r)
            ROWNUM="$OPTARG";;
        ?)
            echo "Usage: `basename $0` -d "搜索目录" -t "搜索文件类型" -f "抽样文件个数" -r "抽样行数""
    esac
done

optnum=$(($OPTIND - 1))

shift $(($OPTIND - 1))

if [ $optnum -ne 8 ];then
        echo "Usage: `basename $0` -d "搜索目录" -t "搜索文件类型" -f "抽样文件个数" -r "抽样行数"
                        在某个目录下随机抽取某种类型的文件若干个，每个文件抽取若干条记录，输出记录"
        exit
fi

rm -rf sampling.txt
for i in `ls $DIR|awk -v t=$TYPE 'BEGIN{FS="_"} {if ($10==t) {print $0}}'|shuf -n$FILENUM`
do
        echo $i
        #zcat $DIR$i|shuf -n$ROWNUM >> sampling.txt
                tar zxvf $DIR"/"$i|xargs cat|shuf -n$ROWNUM >> sampling.txt
                tar zxvf $DIR"/"$i|xargs rm -f
done

rm -f IuCS.list
ls $DIR|awk -v d=$DIR 'BEGIN{FS="_";OFS="/"} {if ($10=="IuCS") {print d,$0}}' >> IuCS.list

echo "successed!see sampling.txt and IuCS.txt"
~