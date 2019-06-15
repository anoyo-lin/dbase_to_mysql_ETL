#!/usr/bin/env python
import dbf
import MySQLdb
import string
from sets import Set
# retreive sequence & outlet_code from current database
conn = MySQLdb.connect(host='192.168.128.1',user='gmm',passwd='infrasys',db='gmmenu',port=3306,charset='utf8')
cur = conn.cursor()
cur.execute("""select menu_id,menu_code from inf_menus where menu_code LIKE 'GMM____'""")
#rec[menu_id][new_menu_code]:menu_code remove GMM
rec=[ list(x) for x in cur]
for x in xrange(0,len(rec)):
	if str(rec[x][1])[:3] == 'GMM':
			rec[x][1] = int(rec[x][1][-4:])

#replace inf_menus,inf_outlets_menus with rec[menu_id][new_menu_code]
for x in rec:
	q1 = """ UPDATE inf_menus SET menu_id = %s where menu_id = %s """
	q2 = """ UPDATE inf_outlets_menus SET outm_menu_id = %s where outm_menu_id = %s """
	data = ( x[1] , x[0] )
	cur.execute(q1,data)
	cur.execute(q2,data)
#UPDATE need commit()
	conn.commit()

#if record is undeleted ,update menu database,else delete records
#view methond t is standing for traditonal display
#update procedure:means if deleted:delete if changed:update if new:insert
#if menu_id is duplicate update the record
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

del_item_dbf=Set()

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
                                	        item_modi1_mlst_id,
                                	        item_modi2_mlst_id,
                                	        item_modi3_mlst_id,
                                	        item_open_price,
                                	        item_open_name
							)
				VALUES 
						(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
						item_modi1_mlst_id=VALUES(item_modi1_mlst_id),
						item_modi2_mlst_id=VALUES(item_modi2_mlst_id),
						item_modi3_mlst_id=VALUES(item_modi3_mlst_id),
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
									x['flist1'],\
									x['flist2'],\
									x['flist3'],\
									x['fopen'],\
									x['ftype'],\
                                	))
	else:
		cur.execute("""DELETE FROM inf_items WHERE item_code = %s""",(x['fitem'],))
		del_item_dbf.add('%d'%int(x['fnum']))
menu.close()
#changed menu_id from 100000+ to outlet_code (GMM0101=>0101)
#meta_lu
for x in rec:
        query = """ UPDATE inf_menu_lookup SET mulu_menu_id = %s where mulu_menu_id = %s """
        data = ( x[1] , x[0] )
        cur.execute(query,data)
        conn.commit()
#sub_lu
for x in rec:
        query = """ UPDATE inf_menu_lookup SET mulu_sub_menu_id = %s where mulu_sub_menu_id = %s """
        data = ( x[1] , x[0] )
        cur.execute(query,data)
        conn.commit()
#delete section 3( not the GMM0101 meta )
cur.execute("""DELETE from inf_menu_lookup where mulu_menu_id > 99999""")

#delete section 1 ( generate lookup from panel.dbf )
cur.execute("""DELETE from inf_menu_lookup where mulu_id < 100000""")

#gen section 2 (only leave the GMM0101 meta and change it sequence to 100000+)
#new order mapping
cur.execute("""select mulu_id,mulu_id from inf_menu_lookup""")
rec=[x for x in cur]
count=100000
for x in xrange(0,len(rec)):
        rec[x][1]=count
	count+=1
#replace mulu_id
for x in rec:
	query = """ UPDATE inf_menu_lookup SET mulu_id = %s where mulu_id = %s """
	data = ( x[1] , x[0] )
	cur.execute(query,data)
	conn.commit
#set table counter to current id
cur.execute("""ALTER TABLE inf_menu_lookup AUTO_INCREMENT=%s""",(count,))
#lookup structure
#0-10000 panel meta_lu ; 10000-20000 GMM0101 meta_lu : 20000-above: sync lookup from gm	
lookup = dbf.Table('./imenu/lookup.dbf')
lookup.open()
#if meta menu delete some content.delete it in user defined menu
del_lu_dbf = Set()
#if user defined menu is same id to meta menu id ,delete it
used_lu_dbf = Set()
#meta menu update,because of its purge every sync,so you wont to bother if sequence will be messed by delete & pack
#insert section 1( panel meta_lu )
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
        	cur.execute(query,(\
								x['fnum'],\
                                x['flu_list'],\
                                x['fnew_lu'],\
                                x['fseq'],\
                                x['fitem'],\
                                x['fsub_menu']\
                                ))
		used_lu_dbf.add('%d'%int(x['flu_list']))
	elif int(x['fnum'].strip()) < 100000 and x['fdeleted'] == True:
		del_lu_dbf.add('%d'%int(x['flu_list']))
#delete dbf_deleted item from section 1 (panel meta_lu) & section 2 (GMM0101 meta_lu)
for x in del_item_dbf:
	cur.execute("""DELETE FROM inf_menu_lookup WHERE mulu_item_id = %s""",(x,))
#delete dbf_deleted lookup from section 1 (panel meta_lu) & section 2 (GMM0101 meta_lu)
for x in del_lu_dbf:
	cur.execute("""DELETE FROM inf_menu_lookup WHERE mulu_menu_id = %s""",(x,))
#delete panel meta_lu from GMM0101 meta_lu lookup
cur.execute("""SELECT mulu_id,mulu_menu_id FROM inf_menu_lookup WHERE mulu_id > 99999""")
rec=[ x for x in cur ]
for x in rec:
	if x[1] in used_lu_dbf:
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
        	cur.execute(query,(\
								x['fnum'],\
                                x['flu_list'],\
                                x['fnew_lu'],\
                                x['fseq'],\
                                x['fitem'],\
                                x['fsub_menu']\
				))
lookup.close()


#purge the category table
cur.execute("""DELETE from inf_item_categories""")

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

del_mod_dbf = Set()

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
		del_mod_dbf.add('%d'%int(x['fnum']))
		cur.execute("""DELETE FROM inf_modifiers WHERE modi_code = %s""",(x['fmod_num'],))

modifier.close()

#changed GMM0101=>0101 in modilist
cur.execute("""SELECT mlst_id,mlst_code FROM inf_modifier_lists WHERE mlst_code LIKE 'GMM____'""")
rec=[ x for x in cur]
for x in xrange(0,len(rec)):
        if str(rec[x][1])[:3] == 'GMM':
                        rec[x][1] = int(rec[x][1][-4:])
for x in rec:
        query = """ UPDATE inf_modifier_lists SET mlst_id = %s where mlst_id = %s """
        data = ( x[1] , x[0] )
        cur.execute(query,data)
        conn.commit()

del_mlu_dbf = Set()

modlsthd = dbf.Table('./imenu/modlsthd.dbf')
modlsthd.open()

for x in modlsthd:
	if x['fdeleted'] == False:
		cur.execute("""INSERT INTO inf_modifier_lists (
				mlst_id,
				mlst_name_l1,
				mlst_name_l2,
				mlst_name_l3,
				mlst_code,
				mlst_min,
				mlst_max
				) 
			VALUES 
				(%s,%s,%s,%s,%s,%s,%s) 
			ON DUPLICATE KEY UPDATE 
				mlst_name_l1=VALUES(mlst_name_l1),
				mlst_name_l2=VALUES(mlst_name_l2),
				mlst_name_l3=VALUES(mlst_name_l3),
				mlst_code=VALUES(mlst_code),
				mlst_min=VALUES(mlst_min),
				mlst_max=VALUES(mlst_max);
			""",(\
						x['fnum'],\
                        x['fmodlstde1'],\
                        x['fmodlstde2'],\
                        x['fmodlstde3'],\
                        x['fmod_list'],\
                        x['fmod_min'],\
                        x['fmod_max'],\
			))
	else:
		del_mlu_dbf.add('%d'%int(x['fnum']))
		cur.execute("""DELETE FROM inf_modifier_lists WHERE mlst_code = %s""",(x['fmod_list'],))
modlsthd.close()

#changed GMM prefix record with outlet 0010 id in modilist

#meta menu
for x in rec:
        query = """ UPDATE inf_modifier_lookup SET mdlu_mlst_id = %s where mdlu_mlst_id = %s """
        data = ( x[1] , x[0] )
        cur.execute(query,data)
        conn.commit()
#sub menu
for x in rec:
        query = """ UPDATE inf_modifier_lookup SET mdlu_sub_mlst_id = %s where mdlu_sub_mlst_id = %s """
        data = ( x[1] , x[0] )
        cur.execute(query,data)
        conn.commit()
#purge the section 2 records
cur.execute("""DELETE FROM inf_modifier_lookup WHERE mdlu_mlst_id > 99999""")

modilist = dbf.Table('./imenu/modilist.dbf')
modilist.open()

for x in modilist:
        query = """INSERT inf_modifier_lookup SET
                                        mdlu_mlst_id = %s,
                                        mdlu_type = %s,
                                        mdlu_seq = %s,
                                        mdlu_modi_id = %s,
                                        mdlu_sub_mlst_id = %s
                                """
        cur.execute(query,(\
                                x['fmod_list'],\
                                x['fnew_list'],\
                                x['fseq'],\
                                x['fmod_num'],\
                                x['fsub_list']\
                                ))
modilist.close()
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

################remove unused modlsthd modifier modilist in record#####################
all_occured_mlu = Set()
meta_mlu = Set()
#all_using_mlu = []
cur.execute("""SELECT item_modi1_mlst_id FROM inf_items""")
for x in cur:
		if x[0] != 0:
			all_occured_mlu.add('%d'%int(x[0]))
			meta_mlu.add('%d'%int(x[0]))
#			all_using_mlu.append('%d'%int(x[0]))
cur.execute("""SELECT item_modi2_mlst_id FROM inf_items""")
for x in cur:
		if x[0] != 0:
			all_occured_mlu.add('%d'%int(x[0]))
			meta_mlu.add('%d'%int(x[0]))
#			all_using_mlu.append('%d'%int(x[0]))
cur.execute("""SELECT item_modi3_mlst_id FROM inf_items""")
for x in cur:
		if x[0] != 0:
			all_occured_mlu.add('%d'%int(x[0]))
			meta_mlu.add('%d'%int(x[0]))
#			all_using_mlu.append('%d'%int(x[0]))
#remove 0
#if 0 in all_occured_mlu:
#	all_occured_mlu.remove(0)
#add 997's cms id
cur.execute("""SELECT mlst_id FROM inf_modifier_lists WHERE mlst_code = '997'""")
for x in cur:
        all_occured_mlu.add('%d'%int(x[0]))
	meta_mlu.add('%d'%int(x[0]))
#	all_using_mlu.append('%d'%int(x[0]))
#add 999's cms_id
cur.execute("""SELECT mlst_id FROM inf_modifier_lists WHERE mlst_code = '999'""")
for x in cur:
        all_occured_mlu.add('%d'%int(x[0]))
	meta_mlu.add('%d'%int(x[0]))
#	all_using_mlu.append('%d'%int(x[0]))
#add one level lower sub menu to set until there is no lower sub menu with while loop
while 1:
	temp = Set()
	length = len(all_occured_mlu)
	for x in all_occured_mlu:
		cur.execute("""SELECT mdlu_sub_mlst_id FROM inf_modifier_lookup WHERE mdlu_mlst_id = %s AND mdlu_type = 'm'""",(x,))
		for y in cur:
			if y[0] != 0:
				temp.add('%d'%int(y[0]))
	all_occured_mlu |= temp
	if length == len(all_occured_mlu):
		break
#str=0
#while str < len(all_using_mlu):
#	temp=[]
#	cur.execute("""SELECT mdlu_sub_mlst_id,mdlu_mlst_id FROM inf_modifier_lookup WHERE mdlu_mlst_id = %s AND mdlu_type = 'm'""",(all_using_mlu[str],))
#	for y in cur:
#		if y[0] != 0 and y[0] != y[1]:
#			temp.append('%d'%int(y[0]))
#	all_using_mlu.extend(temp)
#	str+=1
#occur_cnt=[]
#for i in all_occured_mlu:
#	occur_cnt.append([all_using_mlu.count(i),i])
#occur_cnt.sort()
#occur_cnt.reverse()
all_mlu = Set()
cur.execute("""SELECT mlst_id FROM inf_modifier_lists WHERE mlst_id > 99999""")
for x in cur:
	all_mlu.add('%d'%int(x[0]))
all_mlu |= del_mlu_dbf
all_mlu -= all_occured_mlu
for x in all_mlu:
	cur.execute("""DELETE FROM inf_modifier_lists WHERE mlst_id = %s""",(x,))
	cur.execute("""DELETE FROM inf_modifier_lookup WHERE mdlu_mlst_id = %s""",(x,))
	cur.execute("""DELETE FROM inf_modifier_lookup WHERE mdlu_sub_mlst_id = %s""",(x,))

all_mlu_mod = Set()
cur.execute("""SELECT mdlu_modi_id FROM inf_modifier_lookup""")
for x in cur:
	all_mlu_mod.add('%d'%int(x[0]))
all_mod = Set()
cur.execute("""SELECT modi_id FROM inf_modifiers""")
for x in cur:
	all_mod.add('%d'%int(x[0]))
all_mod |= del_mod_dbf
all_mod -= all_mlu_mod
for x in all_mod:
	cur.execute("""DELETE FROM inf_modifiers WHERE modi_id = %s""",(x,))
################remove unused modlsthd modifier modilist in record#####################

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

###################eliminate all nested modifer sub list in record#####################
#print meta_mlu
def nest(master,all_mod,occured):
	all_mlu=[]
	occured.add(master)
#	print "1st",master
	cur.execute("""SELECT mdlu_modi_id,mdlu_sub_mlst_id FROM inf_modifier_lookup WHERE mdlu_mlst_id = %s """,(master,))
	for sub_col in cur:
		if sub_col[0] not in all_mod:
			all_mod.append(sub_col[0])

		if sub_col[1] not in all_mlu:
			all_mlu.append(sub_col[1])
#	print "2ed",all_mlu
	if len(all_mlu) == 1:
#		print all_mod
		return all_mod
	else:
		for child_mlu in all_mlu:
#			print "next",child_mlu
			if child_mlu not in occured and child_mlu != 0:
				occured.add(child_mlu)
#				print "filter",child_mlu
				nest(child_mlu,all_mod,occured)
		return all_mod
for x in meta_mlu:
	mod=[]
	occ=Set()
	seq=1
	for y in nest(x,mod,occ):
		if seq == 1:
			cur.execute("""DELETE FROM inf_modifier_lookup WHERE mdlu_mlst_id = %s""",(x,))
		cur.execute("""INSERT INTO inf_modifier_lookup (
								mdlu_mlst_id,
								mdlu_type,
								mdlu_seq,
								mdlu_modi_id,
								mdlu_sub_mlst_id
								)VALUES(%s,%s,%s,%s,%s)
								""",(\
									x,\
									'',\
									seq,\
									y,\
									'0'\
								))
		seq+=1
#	print "over"
cur.execute("""SELECT mdlu_mlst_id FROM inf_modifier_lookup""")
#all_last = Set()
#for x in cur:
#	all_last.add('%d'%int(x[0]))
#all_last -= meta_mlu
#print all_last
for x in cur:
	if '%d'%int(x[0]) not in meta_mlu:
		cur.execute("""DELETE FROM inf_modifier_lookup WHERE mdlu_mlst_id = %s""",(x,))
cur.execute("""SELECT mlst_id FROM inf_modifier_lists""")
for x in cur:
	if '%d'%int(x[0]) not in meta_mlu:
		cur.execute("""DELETE FROM inf_modifier_lists WHERE mlst_id = %s""",(x,))
#set the sequence of all records
cur.execute("""SELECT mdlu_id,mdlu_id FROM inf_modifier_lookup""")
rec=[]
rec=[list(x) for x in cur]
count=1
for x in xrange(0,len(rec)):
	rec[x][1]=count
        count+=1
for x in rec:
	query = """ UPDATE inf_modifier_lookup SET mdlu_id = %s where mdlu_id = %s """
	data = ( x[1] , x[0] )
	cur.execute(query,data)
#save changed data
	conn.commit
#set counter
cur.execute("""ALTER TABLE inf_modifier_lookup AUTO_INCREMENT=%s""",(count,))
###################eliminate all nested modifer sub list in record#####################

#delete some duplicate record from inf_menu delete the upper one 
cur.execute("""DELETE t1 FROM inf_menus t1,inf_menus t2 
		WHERE t1.menu_id > t2.menu_id AND t1.menu_code = t2.menu_code""")

cur.execute("""DELETE t1 FROM inf_items t1,inf_items t2 
		WHERE t1.item_id > t2.item_id AND t1.item_code = t2.item_code""")

cur.execute("""DELETE t1 FROM inf_modifiers t1,inf_modifiers t2 
		WHERE t1.modi_id > t2.modi_id AND t1.modi_code = t2.modi_code""")

cur.execute("""DELETE t1 FROM inf_modifier_lists t1,inf_modifier_lists t2 
		WHERE t1.mlst_id > t2.mlst_id AND t1.mlst_code = t2.mlst_code""")

cur.execute("""DELETE t1 FROM inf_item_categories t1,inf_item_categories t2 
		WHERE t1.icat_id > t2.icat_id AND t1.icat_code = t2.icat_code""")

cur.execute("""DELETE t1 FROM inf_menu_lookup t1,inf_menu_lookup t2 
		WHERE t1.mulu_id > t2.mulu_id AND 
		t1.mulu_menu_id = t2.mulu_menu_id AND 
		t1.mulu_seq = t2.mulu_seq AND 
		t1.mulu_item_id = t2.mulu_item_id AND
		t1.mulu_sub_menu_id = t2.mulu_sub_menu_id
		""")

cur.execute("""DELETE t1 FROM inf_modifier_lookup t1,inf_modifier_lookup t2 
		WHERE t1.mdlu_id > t2.mdlu_id AND 
		t1.mdlu_mlst_id = t2.mdlu_mlst_id AND 
		t1.mdlu_seq = t2.mdlu_seq AND 
		t1.mdlu_modi_id = t2.mdlu_modi_id AND
		t1.mdlu_sub_mlst_id = t2.mdlu_sub_mlst_id
		""")
	
		
cur.close()
conn.close()
