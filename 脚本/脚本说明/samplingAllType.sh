#!/bin/bash
while getopts 'd:t:f:r:' OPT; do
    case $OPT in
        d)
            DIR="$OPTARG";;
        f)
            FILENUM="$OPTARG";;
        r)
            ROWNUM="$OPTARG";;
        ?)
            echo "Usage: `basename $0` -d "搜索目录"  -f "每种类型抽样文件个数" -r "每个文件抽样行数""
    esac
done

optnum=$(($OPTIND - 1))

shift $(($OPTIND - 1))

if [ $optnum -ne 6 ];then
        echo "Usage: `basename $0` -d "搜索目录"  -f "每种类型抽样文件个数" -r "每个文件抽样行数"
                在某个目录下随机抽取各种类型的文件若干个，输出抽样文件列表 "
        exit
fi

rm -rf allType.sampling


for line in `ls $DIR|awk 'BEGIN{FS="_";OFS="|"} {array[$10]++} END{for(i in array) print i,array[i]}'`
do
        t=`echo $line|cut -d "|" -f 1`
        n=`echo $line|cut -d "|" -f 2`
        if [ $n -lt $FILENUM ];then
                echo "$t类型的文件数量$t少于抽样数量$FILENUM"
        else
                echo "*$t ok"
                for file in `ls $DIR|awk -v t=$t 'BEGIN{FS="_"} {if ($10==t) {print $0}}'|shuf -n$FILENUM`
                do
                        r=`zcat $DIR$file|wc -l`
                        echo "$t类型，该文件行数为:$r，文件名为:$file"
                        if [ $r -lt $ROWNUM ];then
                                echo "$file的行数为$r，少于抽样行数$ROWNUM，因此只抽样$r行"
                                tar zxvf $DIR$file|xargs cat|awk -v t=$t 'BEGIN{FS="|"} {printf "%s@%s|",t,NF;print $0}' >> allType.sampling
                                tar zxvf $DIR$file|xargs rm -f
                        else
                                tar zxvf $DIR$file|xargs cat|shuf -n$ROWNUM|awk -v t=$t 'BEGIN{FS="|"} {printf "%s@%s|",t,NF;print $0}' >> allType.sampling
                               # tar zxvf $DIR$file|xargs cat>>hi.txt
                                tar zxvf $DIR$file|xargs rm -f
                        fi
                done
        fi
done
echo "successed! see allType.sampling"