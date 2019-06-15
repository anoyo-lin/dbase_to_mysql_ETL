#!/usr/bin/env python
import dbf
import MySQLdb
import string
from sets import Set

conn = MySQLdb.connect(host='192.168.128.1',user='gmm',passwd='infrasys',db='gmmenu',port=3306,charset='utf8')
# retreive sequence & outlet_code from current database
cur = conn.cursor()
cur.execute("""select menu_id,menu_code from inf_menus where menu_code LIKE 'GMM____'""")
rec=[list(x) for x in cur]
for x in xrange(0,len(rec)):
	if str(rec[x][1])[:3] == 'GMM':
			rec[x][1] = int(rec[x][1][-4:])
#filter GMM0010 & removed GMM prefix 
#replace 100000 to 0010 in menu database & outlet_menu database
for x in rec:
	q1 = """ UPDATE inf_menus SET menu_id = %s where menu_id = %s """
	q2 = """ UPDATE inf_outlets_menus SET outm_menu_id = %s where outm_menu_id = %s """
	data = ( x[1] , x[0] )
	cur.execute(q1,data)
	cur.execute(q2,data)
	conn.commit()

#if record is undeleted ,update menu database,else delete records
#view methond t is standing for traditonal display
#update procedure means if deleted insert if changed update if need to delete ,delete it
lu_head = dbf.Table('./imenu/lu_head.dbf')
lu_head.open()
for x in lu_head:
	if x['fdeleted'] == False:
		cur.execute("""INSERT INTO inf_menus (
					menu_id,
					menu_name_l1,
					menu_name_l2,
					menu_name_l3,
					menu_code,
					menu_view_method
					)
				VALUES 
					(%s,%s,%s,%s,%s,%s)
				ON DUPLICATE KEY UPDATE 
					menu_name_l1=VALUES(menu_name_l1),
					menu_name_l2=VALUES(menu_name_l2),
					menu_name_l3=VALUES(menu_name_l3),
					menu_code=VALUES(menu_code)
				""",(\
				x['fnum'],\
                        	x['flu_desc1'],\
                        	x['flu_desc2'],\
                        	x['flu_desc3'],\
                        	x['flu_list'],\
                        	x['fview_meth'],\
				))
	else:
		cur.execute("""DELETE FROM inf_menus WHERE menu_code = %s""",(x['flu_list'],))
lu_head.close()

del_item=Set()

menu = dbf.Table('./imenu/menu.dbf')
menu.open()

for x in menu:
	if x['fdeleted'] == False:
		cur.execute("""INSERT INTO inf_items(
						item_id,
                                	        item_code,
	                                        item_name_l1,
        	                                item_name_l2,
                	                        item_name_l3,
                        	                item_icat_id,
                                	        item_price,
                                	        item_price1,
                                	        item_price2,
                                	        item_price3,
                                	        item_price4,
                                	        item_price5,
                                	        item_open_price,
                                	        item_open_name
							)
				VALUES 
						(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
				ON DUPLICATE KEY UPDATE
						item_code=VALUES(item_code),
						item_name_l1=VALUES(item_name_l1),
						item_name_l2=VALUES(item_name_l2),
						item_name_l3=VALUES(item_name_l3),
						item_icat_id=VALUES(item_icat_id),
						item_price=VALUES(item_price),
						item_price1=VALUES(item_price1),
						item_price2=VALUES(item_price2),
						item_price3=VALUES(item_price3),
						item_price4=VALUES(item_price4),
						item_price5=VALUES(item_price5),
						item_open_price=VALUES(item_open_price),
						item_open_name=VALUES(item_open_name);
					""",(\
					x['fnum'],\
                               		x['fitem'],\
                                	x['fdesc1'],\
                                	x['fdesc2'],\
                                	x['fdesc3'],\
                                	x['fcat'],\
                                	x['fprice1'],\
                                	x['fprice1'],\
                                	x['fprice2'],\
                                	x['fprice3'],\
                                	x['fprice4'],\
                                	x['fprice5'],\
									x['fopen'],\
									x['ftype'],\
                                	))
	else:
		cur.execute("""DELETE FROM inf_items WHERE item_code = %s""",(x['fitem'],))
		del_item.add(x['fitem'])
menu.close()
#changed 100000 to 0010 in lookup database
for x in rec:
        query = """ UPDATE inf_menu_lookup SET mulu_menu_id = %s where mulu_menu_id = %s """
        data = ( x[1] , x[0] )
        cur.execute(query,data)
        conn.commit()

for x in rec:
        query = """ UPDATE inf_menu_lookup SET mulu_sub_menu_id = %s where mulu_sub_menu_id = %s """
        data = ( x[1] , x[0] )
        cur.execute(query,data)
        conn.commit()
#delete the unchanged record didnt contained GMM prefix
#delete section 3
cur.execute("""DELETE from inf_menu_lookup where mulu_menu_id > 99999""")
#delete meta menu lookup from panel information
#delete section 1
cur.execute("""DELETE from inf_menu_lookup where mulu_id < 100000""")

#re-order the residue record to a fluent sequence
#first generate a lookup list with new sequence
cur.execute("""select mulu_id,mulu_id from inf_menu_lookup""")
rec=[list(x) for x in cur]
count=100000
for x in xrange(0,len(rec)):
        rec[x][1]=count
	count+=1
#second update new sequence
for x in rec:
	query = """ UPDATE inf_menu_lookup SET mulu_id = %s where mulu_id = %s """
	data = ( x[1] , x[0] )
	cur.execute(query,data)
	conn.commit
#set table counter to current id
cur.execute("""ALTER TABLE inf_menu_lookup AUTO_INCREMENT=%s""",(count,))
#lookup structure
#0-10000 meta menu lookup ; 10000-20000 user defined menu lookup : 20000-above: sync lookup from gm	
lookup = dbf.Table('./imenu/lookup.dbf')
lookup.open()
#if meta menu delete some content.delete it in user defined menu
ans = Set()
#if user defined menu is same id to meta menu id ,delete it
used = Set()
#meta menu update,because of its purge every sync,so you wont to bother if sequence will be messed by delete & pack
#insert section 1
for x in lookup:
	if int(x['fnum'].strip()) < 100000 and x['fdeleted'] != True:
        	query = """INSERT inf_menu_lookup (
					mulu_id, 
                                        mulu_menu_id,
                                        mulu_type,
                                        mulu_seq,
                                        mulu_item_id,
                                        mulu_sub_menu_id
					)
				VALUES
					(%s,%s,%s,%s,%s,%s)
				ON DUPLICATE KEY UPDATE 
					mulu_menu_id=VALUES(mulu_menu_id),
					mulu_type=VALUES(mulu_type),
					mulu_seq=VALUES(mulu_seq),
					mulu_item_id=VALUES(mulu_item_id),
					mulu_sub_menu_id=VALUES(mulu_sub_menu_id);
				"""
        	cur.execute(query,(x['fnum'],\
                                x['flu_list'],\
                                x['fnew_lu'],\
                                x['fseq'],\
                                x['fitem'],\
                                x['fsub_menu']\
                                ))
		used.add(x['flu_list'])
	elif int(x['fnum'].strip()) < 100000 and x['fdeleted'] == True:
		ans.add(x['flu_list'])
#delete the deleted meta menus & deleted items from the section 2 userdefined menu content
for x in ans:
	cur.execute("""DELETE FROM inf_menu_lookup WHERE mulu_menu_id = %s""",(x,))
for x in del_item:
	cur.execute("""DELETE FROM inf_menu_lookup WHERE mulu_item_id = %s""",(x,))
rec=[]
#delete the meta menu_id record from section 2
cur.execute("""SELECT mulu_id,mulu_menu_id FROM inf_menu_lookup WHERE mulu_id > 99999""")
rec=(tuple(x) for x in cur)
for x in rec:
	if x[1] in used:
		cur.execute("""DELETE FROM inf_menu_lookup WHERE mulu_id = %s""",(x[0],))
#insert section 3
for x in lookup:
	if int(x['fnum'].strip()) > 199999:
        	query = """INSERT inf_menu_lookup (
					mulu_id, 
                                        mulu_menu_id,
                                        mulu_type,
                                        mulu_seq,
                                        mulu_item_id,
                                        mulu_sub_menu_id
					)
				VALUES
					(%s,%s,%s,%s,%s,%s)
				ON DUPLICATE KEY UPDATE 
					mulu_menu_id=VALUES(mulu_menu_id),
					mulu_type=VALUES(mulu_type),
					mulu_seq=VALUES(mulu_seq),
					mulu_item_id=VALUES(mulu_item_id),
					mulu_sub_menu_id=VALUES(mulu_sub_menu_id);
				"""
        	cur.execute(query,(x['fnum'],\
                                x['flu_list'],\
                                x['fnew_lu'],\
                                x['fseq'],\
                                x['fitem'],\
                                x['fsub_menu']\
				))
lookup.close()


#purge the category table
cur.execute('DELETE from inf_item_categories')

category = dbf.Table('./imenu/category.dbf')
category.open()

for x in category:
        query = """INSERT inf_item_categories SET icat_id = %s,
                                        icat_code = %s,
                                        icat_name_l1 = %s,
                                        icat_name_l2 = %s,
                                        icat_name_l3 = %s
                                """
        cur.execute(query,(x['fnum'],\
                                x['fcat_num'],\
                                x['fcat_des1'],\
                                x['fcat_des2'],\
                                x['fcat_des3']\
                                ))
category.close()

modi = Set()
modilist = dbf.Table('./imenu/modilist.dbf')
modilist.open()
for x in modilist:
	if x['fnew_list'] != 'm':
		modi.add('%d' % int(x['fmod_num']))
modilist.close()

del_mod = Set()
modifier = dbf.Table('./imenu/modifier.dbf')
modifier.open()

for x in modifier:
	if x['fdeleted'] == False:
		cur.execute("""INSERT INTO inf_modifiers(
					modi_id,
					modi_code,
					modi_name_l1,
					modi_name_l2,
					modi_name_l3,
					modi_price,
					modi_price1,
					modi_price2,
					modi_price3,
					modi_price4,
					modi_price5,
					modi_operator
						)
			VALUES 
					(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
			ON DUPLICATE KEY UPDATE
					modi_code=VALUES(modi_code),
					modi_name_l1=VALUES(modi_name_l1),
					modi_name_l2=VALUES(modi_name_l2),
					modi_name_l3=VALUES(modi_name_l3),
					modi_price=VALUES(modi_price),
					modi_price1=VALUES(modi_price1),
					modi_price2=VALUES(modi_price2),
					modi_price3=VALUES(modi_price3),
					modi_price4=VALUES(modi_price4),
					modi_price5=VALUES(modi_price5),
					modi_operator=VALUES(modi_operator);
				""",(\
				x['fnum'],\
				x['fmod_num'],\
				x['fmod_desc1'],\
				x['fmod_desc2'],\
				x['fmod_desc3'],\
				x['fmod_pri1'],\
				x['fmod_pri1'],\
				x['fmod_pri2'],\
				x['fmod_pri3'],\
				x['fmod_pri4'],\
				x['fmod_pri5'],\
				x['foperator'],\
				))
	else:
		del_mod.add('%d' % int(x['fnum']))
		cur.execute("""DELETE FROM inf_modifiers WHERE modi_code = %s""",(x['fmod_num'],))

modifier.close()

full_mod = Set()
cur.execute("""SELECT modi_id FROM inf_modifiers""")
for x in cur:
	full_mod.add('%d' % int(x[0]))
full_mod |= del_mod
full_mod -= modi
for x in full_mod:
	cur.execute("""DELETE FROM inf_modifiers WHERE modi_id = %s""",(x,))

#changed GMM prefix record with outlet 0010 id in modlsthd

rec=[]
cur.execute("""SELECT mlst_id,mlst_code FROM inf_modifier_lists WHERE mlst_code LIKE 'GMM____'""")
rec=[list(x) for x in cur]
for x in xrange(0,len(rec)):
        if str(rec[x][1])[:3] == 'GMM':
                        rec[x][1] = int(rec[x][1][-4:])
for x in rec:
        query = """ UPDATE inf_modifier_lists SET mlst_id = %s where mlst_id = %s """
        data = ( x[1] , x[0] )
        cur.execute(query,data)
        conn.commit()

#########################sync image with plu prefix in name############################

inf_images = dbf.Table('./imenu/inf_images.dbf','\
			imgo_by C(1);\
			imgo_out C(6);\
			imgo_meu C(6);\
			imgo_itm C(6);\
			imgo_att C(6);\
			imgo_for C(3);\
			imgo_seq C(3);\
			imgag_id C(6);\
			imgo_lan C(3)',\
			codepage='cp936'\
			)
rec=[]
#plu or plu+name.jpg will be selected 
cur.execute("""select imag_id,imag_title_l1 from inf_images where imag_title_l1 regexp '^[0-9A-Z]{4}[^0-9A-Z]*'""")
rec=[list(x) for x in cur]
#remove suffix
for x in xrange(0,len(rec)):
		rec[x][1] = rec[x][1][:4] 
#		print rec[x][1]
db = dbf.Table('./imenu/menu.dbf')
db.open()
plu=[]
#changed plu to cms id
for x in db:
	plu.append((x['fitem'],x['fnum']))
db.close()
for x in xrange(0,len(rec)):
	for y in plu:
		if rec[x][1] == y[0]:
			rec[x][1] = '%06d' % int(y[1])
			break
#delete some unchanged plu from 4 to 6,deleted 4
cnt=0
while 1:
	if cnt == len(rec):
		break
	if len(rec[cnt][1].strip()) != 6:
		del rec[cnt]
		cnt-=1
	cnt+=1

img=[]
counter=3
for x in rec:
		for y in img:
			if x[1] == y[3]:
				counter+=1
		counter/=3
		img.append((	'i',\
			'0',\
			'0',\
			'%6s' % x[1],\
			'0',\
			'm',\
			'%s'%counter,\
			'%06d' % int(x[0]),\
			'0'\
			))
		img.append((	'i',\
			'0',\
			'0',\
			'%6s' % x[1],\
			'0',\
			't',\
			'%s'%counter,\
			'%06d' % int(x[0]),\
			'0'\
			))
		img.append((	'i',\
			'0',\
			'0',\
			'%6s' % x[1],\
			'0',\
			'p',\
			'%s'%counter,\
			'%06d' % int(x[0]),\
			'0'\
			))
		counter=3
		
rec=[]
cur.execute("""select imag_id,imag_title_l1 from inf_images where imag_title_l1 regexp '^[\@][0-9A-Z]{3}[^0-9A-Z]*'""")
rec=[list(x) for x in cur]
for x in xrange(0,len(rec)):
		rec[x][1] = rec[x][1][1:4] 
#		print rec[x][1]
db = dbf.Table('./imenu/lu_head.dbf')
db.open()
plu=[]
for x in db:
	plu.append((x['flu_list'],x['fnum']))
db.close()
for x in xrange(0,len(rec)):
	for y in plu:
		if rec[x][1] == y[0]:
			rec[x][1] = '%06d' % int(y[1])
			break
cnt=0
while 1:
	if cnt == len(rec):
		break
	if len(rec[cnt][1].strip()) != 6:
		del rec[cnt]
		cnt-=1
	cnt+=1
counter=3
for x in rec:
		for y in img:
			if x[1] == y[2]:
# will add three times
				counter+=1
		counter/=3
		img.append((	'm',\
			'0',\
			'%6s' % x[1],\
			'0',\
			'0',\
			'm',\
			'%s'%counter,\
			'%06d' % int(x[0]),\
			'0'\
			))
		img.append((	'm',\
			'0',\
			'%6s' % x[1],\
			'0',\
			'0',\
			't',\
			'%s'%counter,\
			'%06d' % int(x[0]),\
			'0'\
			))
		img.append((	'm',\
			'0',\
			'%6s' % x[1],\
			'0',\
			'0',\
			'p',\
			'%s'%counter,\
			'%06d' % int(x[0]),\
			'0'\
			))
		counter=3
rec=[]
cur.execute("""select imag_id,imag_title_l1 from inf_images where imag_title_l1 regexp '^[\$][0-9A-Z]{4}[^0-9A-Z]*'""")
rec=[list(x) for x in cur]
for x in xrange(0,len(rec)):
		rec[x][1] = rec[x][1][1:5]
#		print rec[x][1]
counter=3
for x in rec:
		for y in img:
			if x[1].strip() == y[1].strip():
				counter+=1
		counter/=3
		img.append((	'o',\
			'%6s' % x[1],\
			'0',\
			'0',\
			'0',\
			'm',\
			'%s'%counter,\
			'%06d' % int(x[0]),\
			'0'\
			))
		img.append((	'o',\
			'%6s' % x[1],\
			'0',\
			'0',\
			'0',\
			't',\
			'%s'%counter,\
			'%06d' % int(x[0]),\
			'0'\
			))
		img.append((	'o',\
			'%6s' % x[1],\
			'0',\
			'0',\
			'0',\
			'p',\
			'%s'%counter,\
			'%06d' % int(x[0]),\
			'0'\
			))
		img.append((	'o',\
			'%6s' % x[1],\
			'0',\
			'0',\
			'0',\
			'l',\
			'%s'%counter,\
			'%06d' % int(x[0]),\
			'0'\
			))
		counter=3
inf_images.open()
for x in img:
	inf_images.append(x)
#delete all from images database
cur.execute("""DELETE from inf_images_objects""")
#set counter to 1
cur.execute("""ALTER TABLE inf_images_objects AUTO_INCREMENT=%s""",(1,))
#insert & update mysql db with dbf
for x in inf_images:
        query = """INSERT inf_images_objects SET
                                        imgo_by = %s,
                                        imgo_olet_id = %s,
                                        imgo_menu_id = %s,
                                        imgo_item_id = %s,
                                        imgo_attr_id = %s,
                                        imgo_used_for = %s,
                                        imgo_seq = %s,
                                        imgo_imag_id = %s,
                                        imgo_lang = %s
                                """
        cur.execute(query,(\
                        x['imgo_by'],\
                        x['imgo_out'],\
                        x['imgo_meu'],\
                        x['imgo_itm'],\
                        x['imgo_att'],\
                        x['imgo_for'],\
                        x['imgo_seq'],\
                        x['imgag_id'],\
                        x['imgo_lan']\
                                ))
inf_images.close()

#cur.execute("""select imgo_id,imgo_id from inf_images_objects""")
#rec=[list(x) for x in cur]
#count=1
#for x in xrange(0,len(rec)):
#        rec[x][1]=count
#	count+=1
#for x in rec:
#	query = """ UPDATE inf_images_objects SET imgo_id = %s where imgo_id = %s """
#	data = ( x[1] , x[0] )
#	cur.execute(query,data)
#	conn.commit
#########################sync image with plu prefix in name############################

sysaddr = dbf.Table('./origin/sysaddr.dbf')
sysaddr.open()
for x in sysaddr:
	if dbf.is_deleted(x) == False:
		cur.execute("""INSERT INTO inf_outlets (
				olet_id,
				olet_name_l1,
				olet_name_l2,
				olet_name_l3,
				olet_code,
				olet_addr_l1,
				olet_addr_l2,
				olet_addr_l3,
				olet_phone,
				olet_them_id,
				olet_date_format)
			VALUES
				(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
			ON DUPLICATE KEY UPDATE
				olet_name_l1=VALUES(olet_name_l1),	
				olet_name_l2=VALUES(olet_name_l2),	
				olet_name_l3=VALUES(olet_name_l3),	
				olet_code=VALUES(olet_code),	
				olet_addr_l1=VALUES(olet_addr_l1),	
				olet_addr_l2=VALUES(olet_addr_l2),	
				olet_addr_l3=VALUES(olet_addr_l3),	
				olet_phone=VALUES(olet_phone),	
				olet_them_id=VALUES(olet_them_id),	
				olet_date_format=VALUES(olet_date_format);
			""",(\
			x['foutlet'],\
			x['fout_desc'],\
			x['fout_desc'],\
			x['fout_desc'],\
			x['foutlet'],\
			x['faddress1'],\
			x['faddress2'],\
			x['fcity'],\
			x['fphone'],\
			'1',\
			'0'\
			))
		cur.execute("""INSERT INTO inf_menus (
					menu_id,
					menu_name_l1,
					menu_name_l2,
					menu_name_l3,
					menu_code,
					menu_view_method
					) 
				VALUES 
					(%s,%s,%s,%s,%s,%s) 
				ON DUPLICATE KEY UPDATE 
					menu_name_l1=VALUES(menu_name_l1),
					menu_name_l2=VALUES(menu_name_l2),
					menu_name_l3=VALUES(menu_name_l3),
					menu_code=VALUES(menu_code);
				""",(\
#use outlet code as id to link the section one lookup extract from panel.dbf
				x['foutlet'],\
                        	x['fout_desc'],\
                        	x['fout_desc'],\
                        	x['fout_desc'],\
                        	'GMM'+x['foutlet'],\
                        	't'\
				))
		cur.execute("""INSERT INTO inf_outlets_menus (
					outm_id,
					outm_olet_id,
					outm_menu_id,
					outm_seq,
					outm_price_level
				)
				VALUES
					(%s,%s,%s,%s,%s)
				ON DUPLICATE KEY UPDATE
					outm_olet_id=VALUES(outm_olet_id),
					outm_menu_id=VALUES(outm_menu_id),
					outm_seq=VALUES(outm_seq),
					outm_price_level=VALUES(outm_price_level);
				""",(\
				x['foutlet'],\
				x['foutlet'],\
				x['foutlet'],\
					'1',\
					'0'\
				))
	else:
		cur.execute("""DELETE FROM inf_outlets_menus WHERE outm_olet_id = %s""",(x['foutlet'],))
		cur.execute("""DELETE FROM inf_menus WHERE menu_id = %s""",(x['foutlet'],))
		cur.execute("""DELETE FROM inf_outlets WHERE olet_code = %s""",(x['foutlet'],))
#delete some duplicate record from inf_menu delete the upper one 
cur.execute("""DELETE t1 FROM inf_menus t1,inf_menus t2 
		WHERE t1.menu_id > t2.menu_id AND t1.menu_code = t2.menu_code""")

cur.execute("""DELETE t1 FROM inf_items t1,inf_items t2 
		WHERE t1.item_id > t2.item_id AND t1.item_code = t2.item_code""")

cur.execute("""DELETE t1 FROM inf_modifiers t1,inf_modifiers t2 
		WHERE t1.modi_id > t2.modi_id AND t1.modi_code = t2.modi_code""")

#cur.execute("""DELETE t1 FROM inf_modifier_lists t1,inf_modifier_lists t2 
#		WHERE t1.mlst_id > t2.mlst_id AND t1.mlst_code = t2.mlst_code""")

cur.execute("""DELETE t1 FROM inf_item_categories t1,inf_item_categories t2 
		WHERE t1.icat_id > t2.icat_id AND t1.icat_code = t2.icat_code""")

cur.execute("""DELETE t1 FROM inf_menu_lookup t1,inf_menu_lookup t2 
		WHERE t1.mulu_id > t2.mulu_id AND 
		t1.mulu_menu_id = t2.mulu_menu_id AND 
		t1.mulu_seq = t2.mulu_seq AND 
		t1.mulu_item_id = t2.mulu_item_id AND
		t1.mulu_sub_menu_id = t2.mulu_sub_menu_id
		""")

#cur.execute("""DELETE t1 FROM inf_modifier_lookup t1,inf_modifier_lookup t2 
#		WHERE t1.mdlu_id > t2.mdlu_id AND 
#		t1.mdlu_mlst_id = t2.mdlu_mlst_id AND 
#		t1.mdlu_seq = t2.mdlu_seq AND 
#		t1.mdlu_modi_id = t2.mdlu_modi_id AND
#		t1.mdlu_sub_mlst_id = t2.mdlu_sub_mlst_id
#		""")
cur.close()
conn.close()
