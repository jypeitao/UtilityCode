#!/bin/bash

usage() {
cat <<- EOF
Usage:
       merge2project.sh dir

EOF

exit 1
}

changed() {
    local original=$1
    local modified=$2
    local sd=`diff $original $modified |grep -P "^[\d]+(,[\d]+)?[c|a|d][\d]+(,[\d]+)?$"`
    echo $sd
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
let total=0
let ct=0
for t in $stringsxml
do
    src=$xmldir/${t:2}
    sd=`changed $t $src`
    if [ -n "$sd" ];then
        let total=$total+1
        id=`echo $sd|grep d`
        if [ -n "$id" ];then
            let ct=$ct+1
            echo -e "\033[31mCannot overwrite $t\033[0m"
        else
            cp $src $t
        fi
    fi
done

echo -e "\033[32mtotal $total files changed. \033[0m"
echo -e "\033[32m$ct files needed manual processing. \033[0m"
echo ""
echo -e "\033[32mgit status to see the changes. \033[0m"



