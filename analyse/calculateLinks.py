#!/usr/bin/env python
# coding:utf8

import time
import math
import sys
reload(sys)
sys.setdefaultencoding( "utf8" )
import jieba.analyse
import MySQLdb
import MySQLdb.cursors

def cosine(s1, s2):
	inner = 0
	count = 0
	for k1, v1 in s1.items():
		for k2, v2 in s2.items():
			# try:
			# 	inner += 10 * v1 * v2 * abs(self.model.similarity(k1.decode('utf8'), k2.decode('utf8')))
			# except Exception, e:
			# 	if k1 == k2:
			# 		inner += 10 * v1 * v2
			# else:
			# 	pass
			# finally:
			# 	count += 1

			count += 1
			if k1 == k2:
				if v1 > v2:
					inner += v1
				else:
					inner += v2
	return float(inner) / (float(count) + 0.000000001)

def sentence2vector(sentence): 
	sentence = jieba.analyse.extract_tags(sentence, topK=999, withWeight=True, allowPOS=())
	result = {}
	for item in sentence:
		result[item[0]] = item[1]
	return result

db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='timeline', port=8889, charset='utf8', cursorclass = MySQLdb.cursors.DictCursor)
db.autocommit(True)
cursor = db.cursor()

cursor.execute("select * from news where keyword='巴黎暴恐'")
news = cursor.fetchall()

links = []
titles = []

for item in news:
	if item['title'] in titles:
		continue
	titles.append(item['title'])

	links.append([item['id'], int(item['timestamp']), item['title'] + item['content']])

count = len(links)
result = {}
minv = 999
maxv = -1
for x in xrange(0, count):
	data_id = links[x][0]
	print x
	for y in xrange(0, count):
		if not links[x][1] / (24 * 3600) == links[y][1] / (24 * 3600):
			continue

		if not result.has_key(str(data_id)):
			result[str(data_id)] = []

		tmp = cosine(sentence2vector(links[x][2]), sentence2vector(links[y][2]))
		if tmp > maxv:
			maxv = tmp
		if tmp < minv:
			minv = tmp
		result[str(data_id)].append([links[y][0], tmp])

print maxv, minv

count = 0

for key, value in result.items():
	tmp = ''
	for item in value:
		item[1] = (float(item[1]) - minv) / (maxv - minv)
		item[1] = math.sqrt(2 * item[1] - item[1] * item[1])
		if item[1] < 0.1:
			continue
		tmp += str(item[0]) + ':' + str(item[1]) + ',' 
		count += 1
	if not tmp == '':
		tmp = tmp[:-1]
	cursor.execute("update news set links=%s where id=%s", [tmp, int(key)])

print count

db.close()
cursor.close()