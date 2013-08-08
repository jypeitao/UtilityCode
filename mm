#!/bin/sh
TEMP='mm_log'
echo $1
./mk -t mm $1 > $TEMP
if [ $? = 0 ]
then
    result=`grep -P "^Install.*" $TEMP | sed s/Install\:\ //`
    for i in $(echo -e ${result//Install\:\ /})
    do
      echo "i=" $i
    
      temp=${result##*ckt89_we_jb2/}
      result=$result" "${temp%/*}
      echo "$result"
      adb remount
      while [ $? -ne 0 ]
      do
        echo "be sure connected phone?"
        read input
        adb remount
      done
      adb push $result
      while [ $? -ne 0 ]
      do
        adb push $result
      done
      rm $TEMP
      echo "OK"
    done
fi
