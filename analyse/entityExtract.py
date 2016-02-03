#!/usr/bin/env python
# coding:utf8
# 提取新闻中的实体（人名和地名）

import sys 
reload(sys)
sys.setdefaultencoding('utf8')
import jieba
import jieba.posseg as pseg
from snownlp import SnowNLP
import MySQLdb
import MySQLdb.cursors
import json

inputFile = '../data/trainset.txt'
fr = open(inputFile, 'r')

jieba.enable_parallel(4)

db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='timeline', port=8889, charset='utf8', cursorclass = MySQLdb.cursors.DictCursor)
db.autocommit(True)
cursor = db.cursor()

print '提取实体信息'
count = 0
titles = []
for line in fr:
	count += 1
	print count

	line = line.rstrip('\n').split('^')
	news_id = line[0]
	title = line[2]
	content = line[5]

	nodes = {}
	links = {}
	forces = {}
	forces['nodes'] = '['
	forces['links'] = '['
	nodeId = 0

	sentences = content.split('。')
	sentences.append(title)

	for item in sentences:
		item = item.replace('\t', '').replace('\n', '').strip()

		if item == '':
			continue

		if item in titles:
			continue
		titles.append(item)

		tpJ = []
		thJ = []
		tpS = []
		thS = []

		words = pseg.cut(item)
		for word, flag in words:
			if flag == 'ns' and not word in tpJ:
				tpJ.append(word)

			if flag == 'nr' and not word in thJ:
				thJ.append(word)

		words = SnowNLP((item).decode('utf8'))	
		for word, flag in words.tags:
			if flag == 'ns' and not word in tpS:
				tpS.append(word)

			if flag == 'nr' and not word in thS:
				thS.append(word)

		tp = list(set(tpJ) & set(tpS))
		th = list(set(thJ) & set(thS))
		tmp = []

		for item in tp:
			if not item in tmp:
				tmp.append(item)
			if not nodes.has_key(item):
				nodes[item] = nodeId
				nodeId += 1
				forces['nodes'] += '{"name": "' + item + '", "group": 1},'

		for item in th:
			if not item in tmp:
				tmp.append(item)
			if not nodes.has_key(item):
				nodes[item] = nodeId
				nodeId += 1
				forces['nodes'] += '{"name": "' + item + '", "group": 2},'

		for x in xrange(0, len(tmp)):
			if not links.has_key(tmp[x]):
				links[tmp[x]] = {}
			for y in xrange(0, len(tmp)):
				if y == x:
					continue
				if not links[tmp[x]].has_key(tmp[y]):
					links[tmp[x]][tmp[y]] = 0
				links[tmp[x]][tmp[y]] += 1

	for key, value in links.items():
		for k, v in value.items():
			if nodes[key] > nodes[k]:
				continue
			forces['links'] += '{"source": ' + str(nodes[key]) + ', "target": ' + str(nodes[k]) + ', "value": ' + str(v) + '},'

	if forces['nodes'][-1] == ',':
		forces['nodes'] = forces['nodes'][:-1]

	if forces['links'][-1] == ',':
		forces['links'] = forces['links'][:-1]

	forces = '{"nodes":' + forces['nodes'] + '], "links": ' + forces['links'] + ']}'
	cursor.execute("update news set knowledge=%s where title=%s",[forces, title])

fr.close()
db.close()
cursor.close()