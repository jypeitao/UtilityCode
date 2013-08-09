#!/bin/sh
TEMP='mm_log'
echo $1
./mk -t mm $1 > $TEMP
if [ $? = 0 ]
then
    result=`grep -P "^Install.*" $TEMP | sed s/Install\:\ //`
    if [ $result = ""]
    then
    echo "Nothing to do"
    else
    for i in $(echo ${result})
    do
      echo "i=" $i
    
      temp=${i##*ckt89_we_jb2/}
      i=$i" "${temp%/*}
      echo "$i"
      #adb remount
      while [ $? -ne 0 ]
      do
        echo "be sure connected phone?"
        read input
        #adb remount
      done
      #adb push $i
      while [ $? -ne 0 ]
      do
        echo $i
        #adb push $i
      done
    done
    #rm $TEMP
    echo "OK"
    fi
fi

