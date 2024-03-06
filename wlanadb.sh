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


ip=`adb  -s $serial shell ifconfig |grep "inet addr:192"`
ip=`echo $ip | grep -P 'addr:[0-9]+.[0-9]+.[0-9]+.[0-9]+' -o`
ip=`echo $ip | grep -P '[0-9]+.[0-9]+.[0-9]+.[0-9]+' -o`
echo $ip

if [ -z "$ip" ]
then
    echo "connect wifi please"
    echo "Usage: `basename $0`  [SERIAL]"  
    exit
fi

adb -s $serial tcpip 5555
adb -s $serial connect $ip
