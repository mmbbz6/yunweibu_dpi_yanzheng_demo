
 ./list.sh -d /data2/JS/20180328/ -t S1MME -s "20180328 21" -c 1
mv filelist filelist1
 ./list.sh -d /data2/JS/20180328/ -t IuCS -s "20180328 21" -c 1
mv filelist filelist2
 ./list.sh -d /data2/JS/20180328/ -t S1U -s "20180328 21" -c 1
mv filelist filelist3
 ./list.sh -d /data2/JS/20180328/ -t Gn -s "20180328 21" -c 1
cat filelist1>>filelist
cat filelist2>>filelist
cat filelist3>>filelist
rm -f filelist1 filelist2 filelist3
