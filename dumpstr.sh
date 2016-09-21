#!/bin/bash
destPath=./dumpstrings/
curPath=./
#filter="(dumpstrings|test|sample|demo|/pdk/|/cts/|/sdk/|proprietary|develop)"
filter="(dumpstrings|test|sample|demo|/external/|/pdk/|/cts/|/sdk/|develop|/Regional/|/ChinaMobile/|/ChinaTelecom/|/ChinaUnicom/)"

if [ $# -ge 1 ]; then
    curPath=$1
fi

stringsxml=`find $curPath -name strings.xml |grep -P "values(-en-rIN|-en-rGB|-en-rUS])?/strings.xml"|grep -viP "$filter"`

for f in $stringsxml
do
    folder=`dirname $f`
    echo -e "\033[32m dumping $f \033[0m"

    if [ ! -d "$destPath$folder" ]; then
          mkdir -p "$destPath$folder"
    fi
    cp $f $destPath$folder
done

echo ""
echo -e "\033[32m Foler named dumpstrings. \033[0m"
echo ""
echo -e "\033[32m DONE! \033[0m"
