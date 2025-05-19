#!/bin/bash

count=`adb devices |grep device$|wc -l`
if [ "$count" == "0" ]
then
    echo no device connceted
    echo "Usage: `basename $0` [SERIAL]"  
    exit
elif [ $count -gt 1 ]
then
    if [ $# -lt 1 ];then
        adb devices
        echo "Usage: `basename $0` [SERIAL]"  
        exit
    else
        serial=$1
    fi
else
    serial=`adb devices |grep device$`
    serial=($serial);
    serial=${serial[0]}
fi

echo ------------
echo $serial
echo ------------

count=`adb devices |grep device$|wc -l`
if [ "$count" == "0" ]
then
    echo device $serial not exist
    echo "Usage: `basename $0`  [SERIAL]"  
    exit
fi



adb -s $serial root
adb -s $serial remount

adb -s $serial shell "setenforce 0"

adb -s $serial shell "rm -rf /data/local/tmp/xrsdk_env_build"

adb -s $serial push libs /data/local/tmp/xrsdk_env_build

adb -s $serial shell "chmod 755 /data/local/tmp/xrsdk_env_build/envBuild.sh; /data/local/tmp/xrsdk_env_build/envBuild.sh"

adb -s $serial shell sync


