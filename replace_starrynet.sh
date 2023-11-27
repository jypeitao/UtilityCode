#!/bin/bash
if [ $# -lt 1 ]  
then  
    echo "Usage: `basename $0` starrynet.apk [SERIAL]"  
    exit  
fi  

count=`adb devices |grep device$|wc -l`
if [ "$count" == "0" ]
then
    echo no device connceted
    echo "Usage: `basename $0` starrynet.apk [SERIAL]"  
    exit
elif [ $count -gt 1 ]
then
    if [ $# -lt 2 ];then
        adb devices
        echo "Usage: `basename $0` starrynet.apk [SERIAL]"  
        exit
    else
        serial=$2
        apkfile=$1
    fi
else
    

    apkfile=$1
    serial=`adb devices |grep device$`
    serial=($serial);
    serial=${serial[0]}
fi

echo ------------
echo $apkfile
echo $serial
echo ------------

count=`adb devices |grep device$|wc -l`
if [ "$count" == "0" ]
then
    echo device $serial not exist
    echo "Usage: `basename $0` starrynet.apk [SERIAL]"  
    exit
fi

if [ ! -f $apkfile ];then
    echo $apkfile not exist
    echo "Usage: `basename $0` starrynet.apk [SERIAL]"  
    exit
fi


adb -s $serial root
adb -s $serial remount

starrynetDir=`adb -s $serial shell ls /system/priv-app/|grep starrynet -i`
echo $starrynetDir
adb -s $serial shell rm -rf /system/priv-app/$starrynetDir/*
adb -s $serial push $apkfile  /system/priv-app/$starrynetDir/

adb -s $serial shell sync
adb -s $serial shell stop
adb -s $serial shell start


