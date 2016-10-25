#!/bin/bash

usage() {
cat <<- EOF
Usage:
       merge2project.sh dir

EOF

exit 1
}

endWithSeparator() {
    local args=$1
    local str=`echo $args |grep -Pv "/$"`
    if [ -z "$str" ];then
        echo 0
    else
        echo 1

    fi 
}

getLength() {
    local args=$1
    local len=`echo ${#args}`
    local ews=`endWithSeparator $args`
    echo $[$len+$ews]
}

if [ $# -ge 1 ]; then
    xmldir=$1
else
    usage
fi

len=`getLength $xmldir`
cd $xmldir
stringsxml=`find . -name *.xml`
xmldir=`pwd`
cd -

for t in $stringsxml
do
    src=$xmldir/${t:2}
    echo $src
    echo $t

    cp $src $t
    
done



