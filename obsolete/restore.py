#!/usr/bin/env python
import dbf
import MySQLdb
import string
from sets import Set
# retreive sequence & outlet_code from current database
conn = MySQLdb.connect(host='192.168.128.1',user='gmm',passwd='infrasys',db='gmmenu',port=3306,charset='utf8')
cur = conn.cursor()
cur.execute("""DELETE FROM inf_stations""")
cur.execute("""ALTER TABLE inf_stations AUTO_INCREMENT=1""")
stat_dbf = dbf.Table('/usr/local/cms_lin/imenu/stations.dbf')
stat_dbf.open()
for x in stat_dbf:
		cur.execute("""INSERT INTO inf_stations (
					stat_id,
					stat_name_l1,
					stat_name_l2,
					stat_name_l3,
					stat_type,
					stat_uuid,
					stat_olet_id,
					stat_them_id
					)
				VALUES 
					(%s,%s,%s,%s,%s,%s,%s,%s)
				ON DUPLICATE KEY UPDATE 
					stat_name_l1=VALUES(stat_name_l1),
					stat_name_l2=VALUES(stat_name_l2),
					stat_name_l3=VALUES(stat_name_l3),
					stat_type=VALUES(stat_type),
					stat_uuid=VALUES(stat_uuid),
					stat_olet_id=VALUES(stat_olet_id),
					stat_them_id=VALUES(stat_them_id)
				""",(\
				x['fid'],\
                        	x['fdesc'],\
                        	x['fdesc'],\
                        	x['fdesc'],\
                        	x['ftype'],\
                        	x['fuuid'],\
                        	x['foutlet'],\
                        	x['fthem'],\
			))
stat_dbf.close()
cur.close()
conn.close()
