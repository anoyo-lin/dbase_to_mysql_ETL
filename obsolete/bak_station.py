#!/usr/bin/env python
import dbf
import MySQLdb
import string
from sets import Set
# retreive sequence & outlet_code from current database
conn = MySQLdb.connect(host='192.168.128.1',user='gmm',passwd='infrasys',db='gmmenu',port=3306,charset='utf8')
cur = conn.cursor()
cur.execute("""SELECT stat_id,stat_name_l1,stat_type,stat_uuid,stat_olet_id,stat_them_id FROM inf_stations""")
stat=[ x for x in cur ]
if len(stat) > 1:
	stat_dbf=dbf.Table('/usr/local/cms_lin/imenu/stations.dbf','\
				fid N(4,0);\
				fdesc C(10);\
				ftype C(1);\
				fuuid C(40);\
				foutlet N(3,0);\
				fthem N(3,0)',\
				codepage='cp936'
			)
	stat_dbf.open()
	for x in stat:
		stat_dbf.append(x)
	stat_dbf.close()
	cur.execute("""DELETE FROM inf_outlets""")
	cur.execute("""DELETE FROM inf_stations""")
	cur.execute("""ALTER TABLE inf_outlets AUTO_INCREMENT=1""")
	cur.execute("""ALTER TABLE inf_stations AUTO_INCREMENT=1""")
	cur.close()
	conn.close()
