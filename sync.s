#!/bin/bash
ACCOUNT=$1
LOCAL=$(cd $(dirname $0) && pwd)
if [ "${ACCOUNT}" = "" ]
then
        echo "Please input the account name"
        echo "For example, /root/sync.s z01"
        exit
fi

start=`date +%s`
rm -rf `ls ${LOCAL}/imenu/|grep -v stations.dbf`
rm ${LOCAL}/origin/* -rf

if [ -f /u/${ACCOUNT}/data/category.dbf ] && \
[ -f /u/${ACCOUNT}/menu/modilist.dbf ] && \
[ -f /u/${ACCOUNT}/menu/modlsthd.dbf ] && \
[ -f /u/${ACCOUNT}/menu/modifier.dbf ] && \
[ -f /u/${ACCOUNT}/menu/menu.dbf ] && \
[ -f /u/${ACCOUNT}/menu/lu_head.dbf ] && \
[ -f /u/${ACCOUNT}/menu/lookup.dbf ] 
then 
	cp /u/${ACCOUNT}/data/category.dbf ${LOCAL}/origin
	cp /u/${ACCOUNT}/data/sysaddr.dbf ${LOCAL}/origin
	cp /u/${ACCOUNT}/menu/modilist.dbf ${LOCAL}/origin
	cp /u/${ACCOUNT}/menu/modlsthd.dbf ${LOCAL}/origin
	cp /u/${ACCOUNT}/menu/modifier.dbf ${LOCAL}/origin
	cp /u/${ACCOUNT}/menu/menu.dbf ${LOCAL}/origin
	cp /u/${ACCOUNT}/menu/lu_head.dbf ${LOCAL}/origin
	cp /u/${ACCOUNT}/menu/lookup.dbf ${LOCAL}/origin
	cd /u/${ACCOUNT}/data/
		for z in `/usr/gm/bin/batch_tool sysaddr.dbf /s:fdef_key|sed 's/^0*//g'`
		do
			cp /u/${ACCOUNT}/menu/panel${z}.dbf ${LOCAL}/origin
		done
	if [ $# -gt 1 ]
	then
		for x in $@ 
		do                                 
			if [ ${x} != $1 ]
			then
				cd ${LOCAL}/origin
				/usr/gm/bin/batch_tool sysaddr.dbf +/u/${x}/data/sysaddr.dbf
				/usr/gm/bin/batch_tool category.dbf +/u/${x}/data/category.dbf
				/usr/gm/bin/batch_tool modilist.dbf +/u/${x}/menu/modilist.dbf
				/usr/gm/bin/batch_tool modlsthd.dbf +/u/${x}/menu/modlsthd.dbf
				/usr/gm/bin/batch_tool modifier.dbf +/u/${x}/menu/modifier.dbf
				/usr/gm/bin/batch_tool menu.dbf +/u/${x}/menu/menu.dbf
				/usr/gm/bin/batch_tool lu_head.dbf +/u/${x}/menu/lu_head.dbf
				/usr/gm/bin/batch_tool lookup.dbf +/u/${x}/menu/lookup.dbf
				cd /u/${x}/data/
					for y in `/usr/gm/bin/batch_tool sysaddr.dbf /s:fdef_key|sed 's/^0*//g'`
					do
						cp /u/${x}/menu/panel${y}.dbf ${LOCAL}/origin
					done
			fi
		done
	fi
	cd ${LOCAL}
	/usr/bin/python ${LOCAL}/obsolete/purge.py
	/usr/bin/python ${LOCAL}/datacon.py
	/usr/bin/python ${LOCAL}/update.py
	/usr/bin/python ${LOCAL}/obsolete/restore.py
	echo "imenu database synchronization complete !"
	end=`date +%s`
	dif=$[ end - start ]
	echo "the script used ${dif} seconds to complete"
	sleep 3
	sync
else
	echo "no specified database to execute,exit!"
	sleep 3
	exit
fi
