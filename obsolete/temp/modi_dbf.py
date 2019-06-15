#!/usr/bin/env python
import dbf
lookup_db = dbf.Table('./imenu/modilist.dbf')
lookup_db.open()
def indexer(record):
	if record.fnew_list != 'm':
		return dbf.DoNotIndex
	return record.fnew_list

while 1:
	index = lookup_db.create_index(indexer)
	lookup=[]
	for rec in index:
		lookup.append((rec.fmod_list,rec.fsub_list))
		dbf.delete(rec)
	if lookup == []:break
	temp=[]
	for sub_list in lookup:
#		idx = lookup_db.create_index(lambda rec: rec.fmod_list)
#		seq = idx.search(match=sub_list[0])
#		tmp = []
#		for len in seq:
#			tmp.append(len.fseq)
#		upper = int(max(tmp)) + 1
		id = lookup_db.create_index(lambda rec: rec.fmod_list)
		flag = id.search(match=sub_list[1])
		for x in flag:
			temp.append(('',\
				sub_list[0],\
				x.fnew_list,\
#				'%6s' % upper,\
				'',\
				x.fmod_num,\
				x.fsub_list\
					))
#			upper+=1
	lookup_db.pack()

	for x in temp:
		lookup_db.append(x)



	for sub_list in lookup:
		counter=1
        	id = lookup_db.create_index(lambda rec: rec.fmod_list)
        	flag = id.search(match=sub_list[0])
		for x in flag:
			dbf.write(x,fseq= '%6s' % counter)
			counter+=1

count = 1
for rec in lookup_db:
       dbf.write(rec,fnum = '%6s' % count)
       count += 1


lookup_db.close()
