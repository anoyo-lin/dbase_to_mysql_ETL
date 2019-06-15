#!/bin/bash

CODEPAGE=cp936
IP=192.168.128.1
MULTI=1.15
ACCOUNT=z01

VER=`uname -r|awk -F- '{print $1}'|awk -F. '{print $3}'`
if [[ $VER == "18" ]]
then
	rpm -ivh mysql/mysql-community-devel-5.7.9-1.el5.i686.rpm
	rpm -ivh mysql/mysql-community-libs-5.7.9-1.el5.i686.rpm
	ldconfig
	source ~/.bash_profile
fi

function valid_ip()
{
        local ip=$1
        local stat=1

        if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]
        then
                OIFS=$IFS
                IFS='.'
                ip=($ip)
                IFS=$OIFS
                [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
                stat=$?
        fi
        return $stat
}

#read -e -p "please input codepage: big5 use cp950; gbk use cp936. eg: " -i cp936 CODEPAGE
#if [[ $CODEPAGE != "cp936" && $CODEPAGE != "cp950" ]]
#then
#	echo "wrong codepage input, exit!"
#	exit
#else
sed -i "s/\(.*CodePage('\).*\(')\)/\1${CODEPAGE}\2/g" ./datacon.py
sed -i "s/\(codepage='\).*\('.*\)/\1${CODEPAGE}\2/g" ./datacon.py
#fi

#read -e -p "please input CORRECT(DOUBLE CHECK) format cms MySQL server 's ip eg: " -i 192.168.42.1 IP
#if ! valid_ip $IP
#then
#	echo "wrong ip address input, exit!"
#	exit
#fi
#read -e -p "if vat is 0.06 service charge is 0.1 then the multiplier is 1*1.1*1.06=1.166 current multiplier is " -i 1.166 MULTI
#if ! [[ $MULTI =~ ^-?[0-9]+([.][0-9]+)?$  && `echo $MULTI'>='1|bc -l` == 1 ]]
#then
#	echo "wrong multiplier input, exit!"
#	exit
#fi
#read -e -p "which account will you to add imenu sync button in gmselect screen? eg: " -i z01 ACCOUNT
#if ! [[ $ACCOUNT =~ z[0-9][0-9] ]]
#then
#	echo "wrong account name input, exit!"
#	exit
#fi

cd python

#tar zxvf Python-2.7.13.tgz
#cd Python-2.7.13
#./configure --prefix=/usr
#make
#make install
#cd ..

tar zxvf pyparsing-2.2.0.tar.gz
cd pyparsing-2.2.0
python setup.py build
python setup.py install
cd ..

tar zxvf six-1.10.0.tar.gz
cd six-1.10.0
python setup.py build
python setup.py install
cd ..

tar zxvf packaging-16.8.tar.gz
cd packaging-16.8
python setup.py build
python setup.py install
cd ..

tar zxvf appdirs-1.4.3.tar.gz
cd appdirs-1.4.3
python setup.py build
python setup.py install
cd ..

unzip setuptools-35.0.1.zip
cd setuptools-35.0.1
python setup.py build
python setup.py install
cd ..

tar zxvf enum34-1.1.6.tar.gz
cd enum34-1.1.6
python setup.py build
python setup.py install
cd ..

tar zxvf aenum-2.0.8.tar.gz
cd aenum-2.0.8
python setup.py build
python setup.py install
cd ..

unzip dbf-0.96.8.zip
cd dbf-0.96.8
sed -i "s/decoder(data)/decoder(data,'replace')/g" dbf/ver_2.py
sed -i "s/encoder(string)/encoder(string,'replace')/g" dbf/ver_2.py
python setup.py build
python setup.py install
cd ..

unzip MySQL-python-1.2.5
cd MySQL-python-1.2.5
python setup.py build
python setup.py install
cd ..

cd ..
sed -i "s/\(.*host='\)[^']*\(.*\)/\1${IP}\2/g" update.py
for x in `ls obsolete/|grep -v mlst|grep -v temp`
do
	sed -i "s/\(.*host='\)[^']*\(.*\)/\1${IP}\2/g" obsolete/$x
done
for x in `ls obsolete/temp/|grep -v modi`
do
	sed -i "s/\(.*host='\)[^']*\(.*\)/\1${IP}\2/g" obsolete/temp/$x
done

sed -i "s/\(^multiplier = \).*/\1${MULTI}/" datacon.py

sed -i "s/'gbk'/'gb18030'/g" /usr/lib/python2.7/encodings/aliases.py

STAT=`sed -n 's/^9.*stattype="\([0-9]\)".*/\1/p' /u/${ACCOUNT}/gm_user.s|awk '{if ( NR == 1 ){print $1}}'`
INF=`sed -n "s/.*${STAT}.*gm_select.*\/\(.*\);;.*/\1/p" /u/${ACCOUNT}/gm_user.s`

if [ ! -f /u/${ACCOUNT}/gm_user.s.imenu ]
then
cp -p /u/${ACCOUNT}/gm_user.s /u/${ACCOUNT}/gm_user.s.imenu
sed -i "/\[7\][)]/,/esac/{s/\(.*${STAT}[)] \).*\(;;.*\)/\1\/usr\/local\/cm_lin\/sync\.s ${ACCOUNT}\2/}" /u/${ACCOUNT}/gm_user.s
fi

array=($(LANG=en sed -n 's/^selection\([0-9]\).*/\1/p' /u/${ACCOUNT}/${INF}))
length=${#array[@]}
id=0
for ((i=0; i<$length; i++))
do
if [ $id -lt ${array[$i]} ]
then
let "id=${array[$i]}"
fi
done

if [ ! -f /u/${ACCOUNT}/${INF}.imenu ]
then
cp -p /u/${ACCOUNT}/${INF} /u/${ACCOUNT}/${INF}.imenu
sed -i "/^selection${id}.*/i selection${id} = 7,7,7\. Synchronize IPAD menu" /u/${ACCOUNT}/${INF}
let "id+=1"
sed -i "s/.*\( = 0,0,0\..*\)/selection${id}\1/" /u/${ACCOUNT}/${INF}
fi

cp ./bin/batch_tool /usr/gm/bin/
chmod 755 /usr/gm/bin/batch_tool

read -p "setup fininshed! press any key to exit this shell!"

