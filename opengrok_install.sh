#! /bin/bash


opengrok_uri=https://github.com/oracle/opengrok/releases/download/1.13.6/opengrok-1.13.6.tar.gz
tomcat_uri=https://dlcdn.apache.org/tomcat/tomcat-10/v10.1.19/bin/apache-tomcat-10.1.19.tar.gz

# Download
axel $opengrok_uri -o opengrok.tar.gz
axel $tomcat_uri -o tomcat.tar.gz


# tomcat
mkdir -p tomcat
tar -C ./tomcat --strip-components=1 -xzf tomcat.tar.gz


# opengrok
mkdir -p ./opengrok/{src,data,dist,etc,log}
tar -C ./opengrok/dist --strip-components=1 -xzf opengrok.tar.gz
cp ./opengrok/dist/doc/logging.properties ./opengrok/etc

cp ./opengrok/dist/lib/source.war tomcat/webapps

cat > ./opengrok/index.sh <<EOF
#! /bin/bash
gNowDir=\$(cd \$(dirname \$0); pwd)
echo \$gNowDir
#set JAVA_OPTS= -Xms8g -Xmx16g
java -Xmx16g \\
    -Djava.util.logging.config.file=\$gNowDir/etc/logging.properties \\
    -jar \$gNowDir/dist/lib/opengrok.jar \\
    -c ctags \
    -s \$gNowDir/src -d \$gNowDir/data -H -P -S -G \
    -W \$gNowDir/etc/configuration.xml -U http://localhost:8080/source \
    -m 1204

EOF


# start
./tomcat/bin/shutdown.sh
sleep 5s
./tomcat/bin/startup.sh

echo
echo -e "\033[32m ------DONE------ \033[0m"
echo -e "\033[32m 1. Add code to opengrok/src \033[0m"
echo -e "\033[32m 2. sh opengrok/index.sh \033[0m"
echo -e "\033[32m 3. http://127.0.0.0:8080/source/ \033[0m"
echo

