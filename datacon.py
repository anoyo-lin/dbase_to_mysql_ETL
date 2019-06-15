#!/usr/bin/env python

import string
import dbf

multiplier = 1.15
if multiplier == 1:
	NDIGITS = 2
else:
	NDIGITS = 0
#modlsthd ismenu? sequence modi_num modhd_num 
mlist = dbf.Table('./origin/modilist.dbf')
mlist.open()
#pack the delete record
mlist.pack()
#simplifed chinese's codepage is cp936
mlist.codepage = dbf.CodePage('cp936')
mli=[]
#format dbf data to a array
#filled zero in menu_num field
for x in mlist:
	if x['fnew_list'] == False:
		mli.append((	'',\
				'%6s' % x['fmod_list'],\
				'',\
				'%6s' % x['fseq'],\
				'%6s' % x['fmod_num'],\
				'%6s' % 0\
			))
	elif x['fnew_list'] == True:
		mli.append((	'',\
				'%6s' % x['fmod_list'],\
				'm',\
				'%6s' % x['fseq'],\
				'%6s' % 0,\
				'%6s' % x['fmod_num']\
			))
	elif len(x['fmod_list'].strip()) == 3:	
		mli.append((	'',\
				'%6s' % x['fmod_list'],\
				'',\
				'%6s' % x['fseq'],\
				'%6s' % x['fmod_num'],\
				'%6s' % 0\
			))
#generate a new database in imenu directory
mlist_tmp = dbf.Table('./imenu/modilist.dbf','\
				fnum C(6);\
				fmod_list C(6);\
				fnew_list C(1);\
				fseq C(6);\
				fmod_num C(6);\
				fsub_list C(6)',\
				codepage='cp936'\
			)
mlist_tmp.open()
#insert the formatted data in mli array to new dbf
for x in mli:
	mlist_tmp.append(x)
mlist_tmp.close()
mlist.close()
#why add a deleted column?
#because when update the dbf to mysql the script only update modifier modlsthd menu lu_head instead of purge mysql andsynchronize a brand new database
#so if you pack or delete dbf first the sequence of item will be messed
#this method will save some capacity and made the script a little faster
modi = dbf.Table('./origin/modifier.dbf')
modi.open()
modi.codepage = dbf.CodePage('cp936')
mod=[]
#write a sequence number in first col
#only support multiplied operator if foperator col is *,then write 11st col with value x
#short circuit judge sentence none=>0 if not round with price x multiplier with nidigts
counter=1
for x in modi:
	if dbf.is_deleted(x):
		if x['foperator'] == '*':
			mod.append(( '%6s'% counter,\
				x['fmod_num'],\
				x['fmod_desc1'],\
				x['fmod_desc2'],\
				x['fmod_desc3'],\
				0 if x['fmod_pri1'] == None else round(x['fmod_pri1']*multiplier,NDIGITS),\
				0 if x['fmod_pri2'] == None else round(x['fmod_pri2']*multiplier,NDIGITS),\
				0 if x['fmod_pri3'] == None else round(x['fmod_pri3']*multiplier,NDIGITS),\
				0 if x['fmod_pri4'] == None else round(x['fmod_pri4']*multiplier,NDIGITS),\
				0 if x['fmod_pri5'] == None else round(x['fmod_pri5']*multiplier,NDIGITS),\
				'x',\
				True\
				))
		else:
			mod.append(( '%6s'% counter,\
				x['fmod_num'],\
				x['fmod_desc1'],\
				x['fmod_desc2'],\
				x['fmod_desc3'],\
				0 if x['fmod_pri1'] == None else round(x['fmod_pri1']*multiplier,NDIGITS),\
				0 if x['fmod_pri2'] == None else round(x['fmod_pri2']*multiplier,NDIGITS),\
				0 if x['fmod_pri3'] == None else round(x['fmod_pri3']*multiplier,NDIGITS),\
				0 if x['fmod_pri4'] == None else round(x['fmod_pri4']*multiplier,NDIGITS),\
				0 if x['fmod_pri5'] == None else round(x['fmod_pri5']*multiplier,NDIGITS),\
				'',\
				True\
			))
	else:
		if x['foperator'] == '*':
			mod.append(( '%6s'% counter,\
				x['fmod_num'],\
				x['fmod_desc1'],\
				x['fmod_desc2'],\
				x['fmod_desc3'],\
				0 if x['fmod_pri1'] == None else round(x['fmod_pri1']*multiplier,NDIGITS),\
				0 if x['fmod_pri2'] == None else round(x['fmod_pri2']*multiplier,NDIGITS),\
				0 if x['fmod_pri3'] == None else round(x['fmod_pri3']*multiplier,NDIGITS),\
				0 if x['fmod_pri4'] == None else round(x['fmod_pri4']*multiplier,NDIGITS),\
				0 if x['fmod_pri5'] == None else round(x['fmod_pri5']*multiplier,NDIGITS),\
				'x',\
				False\
				))
		else:
			mod.append(( '%6s'% counter,\
				x['fmod_num'],\
				x['fmod_desc1'],\
				x['fmod_desc2'],\
				x['fmod_desc3'],\
				0 if x['fmod_pri1'] == None else round(x['fmod_pri1']*multiplier,NDIGITS),\
				0 if x['fmod_pri2'] == None else round(x['fmod_pri2']*multiplier,NDIGITS),\
				0 if x['fmod_pri3'] == None else round(x['fmod_pri3']*multiplier,NDIGITS),\
				0 if x['fmod_pri4'] == None else round(x['fmod_pri4']*multiplier,NDIGITS),\
				0 if x['fmod_pri5'] == None else round(x['fmod_pri5']*multiplier,NDIGITS),\
				'',\
				False\
			))
	counter+=1
modi_tmp = dbf.Table('./imenu/modifier.dbf','\
			fnum C(6);\
			fmod_num C(3);\
			fmod_desc1 C(30);\
			fmod_desc2 C(30);\
			fmod_desc3 C(30);\
			fmod_pri1 N(7,2);\
			fmod_pri2 N(7,2);\
			fmod_pri3 N(7,2);\
			fmod_pri4 N(7,2);\
			fmod_pri5 N(7,2);\
			foperator C(1);\
			fdeleted L',\
			codepage='cp936'\
			)
modi_tmp.open()
for x in mod:
	modi_tmp.append(x)
modi_tmp.close()
modi.close()
#will add a new col to store deleted status?
mhd = dbf.Table('./origin/modlsthd.dbf')
mhd.open()
mhd.codepage = dbf.CodePage('cp936')
mh=[]
counter=100000
for x in mhd:
	if dbf.is_deleted(x):
		mh.append(( '%6s' % counter,\
				x['fmodlstde1'],\
				x['fmodlstde2'],\
				x['fmodlstde3'],\
				x['fmod_list'],\
				x['fmod_min'],\
				x['fmod_max'],\
				True\
			))
	else:
		mh.append(( '%6s' % counter,\
				x['fmodlstde1'],\
				x['fmodlstde2'],\
				x['fmodlstde3'],\
				x['fmod_list'],\
				x['fmod_min'],\
				x['fmod_max'],\
				False\
			))
	counter+=1
mhd_tmp = dbf.Table('./imenu/modlsthd.dbf','\
			fnum C(6);\
			fmodlstde1 C(30);\
			fmodlstde2 C(30);\
			fmodlstde3 C(30);\
			fmod_list C(3);\
			fmod_min N(2,0);\
			fmod_max N(2,0);\
			fdeleted L',\
			codepage='cp936'\
			)
mhd_tmp.open()
for x in mh:
	mhd_tmp.append(x)
for x in mhd_tmp:
                if x['fmod_min'] == None:
                        dbf.write(x,fmod_min=0)
                if x['fmod_max'] == None:
                        dbf.write(x,fmod_max=0)
mhd_tmp.close()
mhd.close()
############################################################
#this section will replace the modi_num & modhd_num with new generated sequence before
#tbl will store replace list
tbl=[]
modi_tmp.open()
for x in modi_tmp:
	tbl.append((x['fmod_num'],x['fnum']))
modi_tmp.close()
mlist_tmp.open()
#if you found the result in tbl,replace the record and BREAK the searching loop
#replaced record will be a 6 digits number
for x in mlist_tmp:
     for y in tbl:
		if x['fmod_num'].strip() == y[0]:
			dbf.write(x,fmod_num='%06d' % int(y[1]))
			break		
mlist_tmp.close()

tbl=[]
mhd_tmp.open()
for x in mhd_tmp:
        tbl.append((x['fmod_list'],x['fnum']))
modi_tmp.close()
mlist_tmp.open()

for x in mlist_tmp:
     for y in tbl:
		if x['fmod_list'].strip() == y[0]:
			dbf.write(x,fmod_list='%06d' % int(y[1]))
			break
for x in mlist_tmp:
     for y in tbl:
		if x['fsub_list'].strip() == y[0]:
			dbf.write(x,fsub_list='%06d' % int(y[1]))
			break
#filter out undefined (didnt replaced) record in dbf
for x in mlist_tmp:
		if len(x['fmod_list'].strip()) == 3:
				dbf.delete(x)
				continue
		if len(x['fmod_num'].strip()) == 3:
				dbf.delete(x)
				continue
		if len(x['fsub_list'].strip()) == 3:
				dbf.delete(x)
#pack the dbf
mlist_tmp.pack()
mlist_tmp.close()
###################################################################
			
menu = dbf.Table('./origin/menu.dbf')
menu.open()
menu.codepage = dbf.CodePage('cp936')
men=[]
counter=1
for x in menu:
	if dbf.is_deleted(x):
		if x['fopen'] == False and x['ftype'] == '2':
			men.append(('%6s'%counter,\
			x['fitem'],\
			x['fdesc1'],\
			x['fdesc2'],\
			x['fdesc3'],\
			'%6s' % x['fcat'],\
			0 if x['fprice1'] == None else round(x['fprice1']*multiplier,NDIGITS),\
			0 if x['fprice2'] == None else round(x['fprice2']*multiplier,NDIGITS),\
			0 if x['fprice3'] == None else round(x['fprice3']*multiplier,NDIGITS),\
			0 if x['fprice4'] == None else round(x['fprice4']*multiplier,NDIGITS),\
			0 if x['fprice5'] == None else round(x['fprice5']*multiplier,NDIGITS),\
			'%6s' % x['flist1'],\
			'%6s' % x['flist2'],\
			'%6s' % x['flist3'],\
			'',\
			'o',\
			True\
		))
		elif x['fopen'] == True and x['ftype'] == '2':
                	men.append(('%6s'%counter,\
                        x['fitem'],\
                        x['fdesc1'],\
                        x['fdesc2'],\
                        x['fdesc3'],\
                        '%6s' % x['fcat'],\
                        0 if x['fprice1'] == None else round(x['fprice1']*multiplier,NDIGITS),\
                        0 if x['fprice2'] == None else round(x['fprice2']*multiplier,NDIGITS),\
                        0 if x['fprice3'] == None else round(x['fprice3']*multiplier,NDIGITS),\
                        0 if x['fprice4'] == None else round(x['fprice4']*multiplier,NDIGITS),\
                        0 if x['fprice5'] == None else round(x['fprice5']*multiplier,NDIGITS),\
                        '%6s' % x['flist1'],\
                        '%6s' % x['flist2'],\
                        '%6s' % x['flist3'],\
                        'o',\
                        'o',\
			True\
                ))

		elif x['fopen'] == True and x['ftype'] != '2':
                	men.append(('%6s'%counter,\
                        x['fitem'],\
                        x['fdesc1'],\
                        x['fdesc2'],\
                        x['fdesc3'],\
                        '%6s' % x['fcat'],\
                        0 if x['fprice1'] == None else round(x['fprice1']*multiplier,NDIGITS),\
                        0 if x['fprice2'] == None else round(x['fprice2']*multiplier,NDIGITS),\
                        0 if x['fprice3'] == None else round(x['fprice3']*multiplier,NDIGITS),\
                        0 if x['fprice4'] == None else round(x['fprice4']*multiplier,NDIGITS),\
                        0 if x['fprice5'] == None else round(x['fprice5']*multiplier,NDIGITS),\
                        '%6s' % x['flist1'],\
                        '%6s' % x['flist2'],\
                        '%6s' % x['flist3'],\
                        'o',\
                        '',\
			True\
                ))
		else:
                	men.append(('%6s'%counter,\
                        x['fitem'],\
                        x['fdesc1'],\
                        x['fdesc2'],\
                        x['fdesc3'],\
                        '%6s' % x['fcat'],\
                        0 if x['fprice1'] == None else round(x['fprice1']*multiplier,NDIGITS),\
                        0 if x['fprice2'] == None else round(x['fprice2']*multiplier,NDIGITS),\
                        0 if x['fprice3'] == None else round(x['fprice3']*multiplier,NDIGITS),\
                        0 if x['fprice4'] == None else round(x['fprice4']*multiplier,NDIGITS),\
                        0 if x['fprice5'] == None else round(x['fprice5']*multiplier,NDIGITS),\
                        '%6s' % x['flist1'],\
                        '%6s' % x['flist2'],\
                        '%6s' % x['flist3'],\
                        '',\
                        '',\
			True\
                ))
                counter+=1
	else:
		if x['fopen'] == False and x['ftype'] == '2':
			men.append(('%6s'%counter,\
			x['fitem'],\
			x['fdesc1'],\
			x['fdesc2'],\
			x['fdesc3'],\
			'%6s' % x['fcat'],\
			0 if x['fprice1'] == None else round(x['fprice1']*multiplier,NDIGITS),\
			0 if x['fprice2'] == None else round(x['fprice2']*multiplier,NDIGITS),\
			0 if x['fprice3'] == None else round(x['fprice3']*multiplier,NDIGITS),\
			0 if x['fprice4'] == None else round(x['fprice4']*multiplier,NDIGITS),\
			0 if x['fprice5'] == None else round(x['fprice5']*multiplier,NDIGITS),\
			'%6s' % x['flist1'],\
			'%6s' % x['flist2'],\
			'%6s' % x['flist3'],\
			'',\
			'o',\
			False\
		))
		elif x['fopen'] == True and x['ftype'] == '2':
                	men.append(('%6s'%counter,\
                        x['fitem'],\
                        x['fdesc1'],\
                        x['fdesc2'],\
                        x['fdesc3'],\
                        '%6s' % x['fcat'],\
                        0 if x['fprice1'] == None else round(x['fprice1']*multiplier,NDIGITS),\
                        0 if x['fprice2'] == None else round(x['fprice2']*multiplier,NDIGITS),\
                        0 if x['fprice3'] == None else round(x['fprice3']*multiplier,NDIGITS),\
                        0 if x['fprice4'] == None else round(x['fprice4']*multiplier,NDIGITS),\
                        0 if x['fprice5'] == None else round(x['fprice5']*multiplier,NDIGITS),\
                        '%6s' % x['flist1'],\
                        '%6s' % x['flist2'],\
                        '%6s' % x['flist3'],\
                        'o',\
                        'o',\
			False\
                ))

		elif x['fopen'] == True and x['ftype'] != '2':
                	men.append(('%6s'%counter,\
                        x['fitem'],\
                        x['fdesc1'],\
                        x['fdesc2'],\
                        x['fdesc3'],\
                        '%6s' % x['fcat'],\
                        0 if x['fprice1'] == None else round(x['fprice1']*multiplier,NDIGITS),\
                        0 if x['fprice2'] == None else round(x['fprice2']*multiplier,NDIGITS),\
                        0 if x['fprice3'] == None else round(x['fprice3']*multiplier,NDIGITS),\
                        0 if x['fprice4'] == None else round(x['fprice4']*multiplier,NDIGITS),\
                        0 if x['fprice5'] == None else round(x['fprice5']*multiplier,NDIGITS),\
                        '%6s' % x['flist1'],\
                        '%6s' % x['flist2'],\
                        '%6s' % x['flist3'],\
                        'o',\
                        '',\
			False\
                ))
		else:
                	men.append(('%6s'%counter,\
                        x['fitem'],\
                        x['fdesc1'],\
                        x['fdesc2'],\
                        x['fdesc3'],\
                        '%6s' % x['fcat'],\
                        0 if x['fprice1'] == None else round(x['fprice1']*multiplier,NDIGITS),\
                        0 if x['fprice2'] == None else round(x['fprice2']*multiplier,NDIGITS),\
                        0 if x['fprice3'] == None else round(x['fprice3']*multiplier,NDIGITS),\
                        0 if x['fprice4'] == None else round(x['fprice4']*multiplier,NDIGITS),\
                        0 if x['fprice5'] == None else round(x['fprice5']*multiplier,NDIGITS),\
                        '%6s' % x['flist1'],\
                        '%6s' % x['flist2'],\
                        '%6s' % x['flist3'],\
                        '',\
                        '',\
			False\
                ))
	        counter+=1
menu_tmp = dbf.Table('./imenu/menu.dbf','fnum C(6);\
					fitem C(4);\
					fdesc1 C(30);\
					fdesc2 C(30);\
					fdesc3 C(30);\
					fcat C(6);\
					fprice1 N(10,2);\
					fprice2 N(10,2);\
					fprice3 N(10,2);\
					fprice4 N(10,2);\
					fprice5 N(10,2);\
					flist1 C(6);\
					flist2 C(6);\
					flist3 C(6);\
					fopen C(1);\
					ftype C(1);\
					fdeleted L',\
					codepage='cp936')
menu_tmp.open()
for x in men:
	menu_tmp.append(x)
menu_tmp.close()
menu.close()

lu_head = dbf.Table('./origin/lu_head.dbf')
lu_head.open()
lu_head.codepage = dbf.CodePage('cp936')
lu=[]
counter=100000
for x in lu_head:
	if dbf.is_deleted(x):
		lu.append(('%6s'%counter,\
			x['flu_desc1'],\
			x['flu_desc2'],\
			x['flu_desc3'],\
			x['flu_list'],\
			't',\
			True\
			))
	else:
		lu.append(('%6s'%counter,\
			x['flu_desc1'],\
			x['flu_desc2'],\
			x['flu_desc3'],\
			x['flu_list'],\
			't',\
			False\
			))
	counter+=1
lu_head_tmp = dbf.Table('./imenu/lu_head.dbf','\
				fnum C(6);\
				flu_desc1 C(30);\
				flu_desc2 C(30);\
				flu_desc3 C(30);\
				flu_list C(3);\
				fview_meth C(1);\
				fdeleted L',\
				codepage='cp936'\
				)
lu_head_tmp.open()
for x in lu:
	lu_head_tmp.append(x)
lu_head_tmp.close()
lu_head.close()

lkp_tmp = dbf.Table('./imenu/lookup.dbf','\
                                fnum C(6);\
                                flu_list C(6);\
                                fnew_lu C(1);\
                                fseq C(2);\
                                fitem C(6);\
                                fsub_menu C(6);\
                                fdeleted L',\
                                codepage='cp936'\
                        )
##################get main menus from panel##################
db = dbf.Table('./origin/sysaddr.dbf')
db.open()
db.codepage = dbf.CodePage('cp936')
outlet=[]
for x in db:
	if dbf.is_deleted(x):
		outlet.append((	x['foutlet'],\
				x['fout_desc'],\
				x['fdef_key'],\
				True))
	else:
		outlet.append((	x['foutlet'],\
				x['fout_desc'],\
				x['fdef_key'],\
				False))
rec=[]
for x in xrange(0,len(outlet)):
	path = str('./origin/panel'+outlet[x][2].strip('0')+'.dbf')
	database = dbf.Table(path)
	database.open()
	database.codepage = dbf.CodePage('cp936')
	for y in database:
		if y['finactive'] != True:
			rec.append((	outlet[x][0],\
					y['fpage'],\
					int(y['fseq']),\
					y['fdesc1'],\
					y['fdesc2'],\
					y['ftype'],\
					y['fnumb'],\
					y['fadd_row'],\
					y['fadd_col'],\
					outlet[x][3]\
					))
	database.close()
#one row contains 6 buttons,this function will remove the hidden buttons from database
#and in case to avoid the extra error if the col & row > 5 .in this situation the hidden button only in same row
elm=[]
for x in rec:
#col & row !=0 and not the rightest button
	if x[7] != 0 or x[8] != 0 and x[2]%6 != 0:
		for y in xrange(0,x[7]+1):
			for z in xrange(0,x[8]+1):
#skip the origin button
				if y == 0 and z == 0 : continue
#only remove same row hidden button
				elif z*1+x[2] <= (x[2]/6+1)*6:
					elm.append((x[0],x[1],y*6+z*1+x[2]))
#remove the elimated list from full rec array
counter = 0
while 1:
	if counter == len(rec):
		break
	for x in elm:
		if rec[counter][0] == x[0] and rec[counter][1] == x[1] and rec[counter][2] == x[2]:
			del rec[counter]
			counter -= 1
			break
	counter += 1
#format the rec to result and only append type 2 (list) type 1 (item) in result
#add a sequence counter in first row
#2nd col contains outlet number
#7rd col contains if it was deleted
result=[]
counter=1
for x in xrange(0,len(rec)):
	if rec[x][5] == '2' and ('0' if rec[x][6].strip() == '' else rec[x][6].strip()) != '0':
		result.append([\
				'%6s'%counter,\
				'%6s'%rec[x][0],\
				'm',\
				'%2s'%0,\
				'0',\
				'%6s'%rec[x][6],\
				rec[x][9]\
				])
		counter+=1
for x in xrange(0,len(rec)):
	if rec[x][5] == '1' and ('0' if rec[x][6].strip() == '' else rec[x][6].strip()) != '0':
		result.append([\
				'%6s'%counter,\
				'%6s'%rec[x][0],\
				'',\
				'%2s'%0,\
				'%6s'%rec[x][6],\
				'0',\
				rec[x][9]\
				])
		counter+=1
#add a sequence info to every record ,but it will add the meta menu later as no.1 in sequence
#so this function will put the first list in sequence 2 and first item in no.1
for x in xrange(0,len(result)):
#this judgement will set counter to 1 if the first one is a item,otherwise it set to 2
	if x == 0:
		if result[x][2] == 'm':
			cnt=2
		else:
			cnt=1
		result[x][3] = '%s'%cnt
		continue
#if same to previous one,increase the counter	
	if result[x-1][1] == result[x][1]:
		cnt+=1
	else:
#if not reset the counter from 2 or 1
		if result[x][2] == 'm':
			cnt=2
		else:
			cnt=1
	result[x][3] = '%s'%cnt
#add the meta list,and keep increasing the counter
for x in outlet:
	if x[3] == True:
		result.append([\
				'%6s'%counter,\
				'%6s'%x[0],\
				'm',\
				'1',\
				'0',\
				'%6s'%x[0],\
				True\
				])
	else:
		result.append([\
				'%6s'%counter,\
				'%6s'%x[0],\
				'm',\
				'1',\
				'0',\
				'%6s'%x[0],\
				False\
				])
	counter += 1

db.close()

lkp_tmp.open()
for x in result:
        lkp_tmp.append(tuple(x))
lkp_tmp.close()

##################get main menus from panel##################
lkp = dbf.Table('./origin/lookup.dbf')
lkp.open()
lkp.pack()
lkp.codepage = dbf.CodePage('cp936')
lk=[]
counter=200000
for x in lkp:
        if x['fnew_lu'] == False:
                lk.append((    '%6s'%counter,\
                                '%6s' % x['flu_list'],\
                                '',\
                                x['fseq'],\
                                '%6s' % x['fitem'],\
                                '%6s' % 0,\
				False\
                        ))
        elif x['fnew_lu'] == True:
                lk.append((    '%6s'%counter,\
                                '%6s' % x['flu_list'],\
                                'm',\
                                x['fseq'],\
                                '%6s' % 0,\
                                '%6s' % x['fitem'],\
				False\
                        ))
	else:
                lk.append((    '%6s'%counter,\
                                '%6s' % x['flu_list'],\
                                '',\
                                x['fseq'],\
                                '%6s' % x['fitem'],\
                                '%6s' % 0,\
				False\
                        ))
	counter+=1
lkp.close()

lkp_tmp.open()
for x in lk:
        lkp_tmp.append(x)
lkp_tmp.close()
#########################################################
tbl=[]
menu_tmp.open()
for x in menu_tmp:
        tbl.append((x['fitem'],x['fnum']))
menu_tmp.close()
lkp_tmp.open()

for x in lkp_tmp:
	for y in tbl:
		if x['fitem'].strip() == y[0]:
			dbf.write(x,fitem='%06d' % int(y[1]))
			break
		
lkp_tmp.close()

tbl=[]
lu_head_tmp.open()
for x in lu_head_tmp:
        tbl.append((x['flu_list'],x['fnum']))
lu_head_tmp.close()
lkp_tmp.open()

for x in lkp_tmp:
	for y in tbl:
		if len(x['flu_list'].strip()) == 3 and x['flu_list'].strip() == y[0]:
			dbf.write(x,flu_list='%06d' % int(y[1]))
			break
for x in lkp_tmp:
	for y in tbl:
		if len(x['fsub_menu'].strip()) == 3 and x['fsub_menu'].strip() == y[0]:
			dbf.write(x,fsub_menu='%06d' % int(y[1]))
			break

for x in lkp_tmp:
		if len(x['flu_list'].strip()) == 3:
				dbf.delete(x)
				continue
		if len(x['fitem'].strip()) == 4:
				dbf.delete(x)
				continue
		if len(x['fsub_menu'].strip()) == 3:
				dbf.delete(x)
lkp_tmp.pack()
lkp_tmp.close()
###################################################################
# replace modhd_num in new menu.dbf
tbl=[]
mhd_tmp.open()
for x in mhd_tmp:
	tbl.append(( x['fmod_list'],x['fnum']))
mhd_tmp.close()
menu_tmp.open()

for x in menu_tmp:
	for y in tbl:
		if x['flist1'].strip() == y[0]:
			dbf.write(x,flist1='%06d' % int(y[1]))
		if x['flist2'].strip() == y[0]:
			dbf.write(x,flist2='%06d' % int(y[1]))
		if x['flist3'].strip() == y[0]:
			dbf.write(x,flist3='%06d' % int(y[1]))
menu_tmp.close()

cat = dbf.Table('./origin/category.dbf')
cat.open()
cat.pack()
cat.codepage = dbf.CodePage('cp936')
ca=[]
counter=1
for x in cat:
	ca.append(( '%6s'%counter,\
		x['fcat_num'],\
		x['fcat_desc'],\
		x['fcat_desc'],\
		x['fcat_desc'],\
		))
	counter+=1
cat_tmp = dbf.Table('./imenu/category.dbf','\
			fnum C(6);\
			fcat_num C(3);\
			fcat_des1 C(20);\
			fcat_des2 C(20);\
			fcat_des3 C(20)',\
			codepage='cp936'\
			)
cat_tmp.open()
for x in ca:
	cat_tmp.append(x)
#replace all category number in new menu.dbf
tbl=[]
for x in cat_tmp:
	tbl.append((x['fcat_num'],x['fnum']))
cat_tmp.close()
cat.close()

menu_tmp.open()
for x in menu_tmp:
	for y in tbl:
		if x['fcat'].strip() == y[0]:
			dbf.write(x,fcat = '%06d' % int(y[1]))
			break
menu_tmp.close()
#filter out unchanged category & modhd_num
#unchanged field is 3 digits but some field dont have record and was None 
#so the judge statment will not equal 6 to consist of extra situatiopn case
menu_tmp.open()
for x in menu_tmp:
		if len(x['fcat'].strip()) != 6:
			dbf.write(x,fcat='%6s' % 0)
		if len(x['flist1'].strip()) != 6:
			dbf.write(x,flist1='%6s' % 0)
		if len(x['flist2'].strip()) != 6:
			dbf.write(x,flist2='%6s' % 0)
		if len(x['flist3'].strip()) != 6:
			dbf.write(x,flist3='%6s' % 0)
menu_tmp.close()
