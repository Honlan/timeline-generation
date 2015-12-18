#!/usr/bin/env python
# coding:utf8

import time
import random
from py2neo import *

authenticate("localhost:7474", "neo4j", "neo931211")
graph = Graph("http://localhost:7474/db/data")

inputFile = "../data/ifeng.txt"
fr = open(inputFile, 'r')

tags = ['新闻背景', '事实陈述', '事件演化', '各方态度', '直接关联', '暂无关联']

graph.cypher.execute("create (paris:Event {name:'巴黎暴恐'}),(t1:Tag {name:'新闻背景'}),(t2:Tag {name:'事实陈述'}),(t3:Tag {name:'事件演化'}),(t4:Tag {name:'各方态度'}),(t5:Tag {name:'直接关联'}),(t6:Tag {name:'暂无关联'}),(paris)-[:TAG]->(t1),(paris)-[:TAG]->(t2),(paris)-[:TAG]->(t3),(paris)-[:TAG]->(t4),(paris)-[:TAG]->(t5),(paris)-[:TAG]->(t6)")

count = 0

result = {}

for line in fr:
	count = count + 1
	print count
	line = line.rstrip('\n').split('^')
	title = line[1]
	timestamp = line[3]

	tag = tags[random.randint(0, 5)]

	if not result.has_key(tag):
		result[tag] = {}
		result[tag][timestamp] = []
		result[tag][timestamp].append(title)
	elif not result[tag].has_key(timestamp):
		result[tag][timestamp] = []
		result[tag][timestamp].append(title)
	else:
		result[tag][timestamp].append(title)

for tag, value in result.items():
	print tag
	for date, titles in value.items():
		print '\t' + date
		graph.cypher.execute("match (t:Tag) where t.name='" + tag + "' create (d:Date {name:'" + date + "', parent:'" + tag + "'}), (t)-[:DATE]->(d)")
		for item in titles:
			print '\t\t' + item
			graph.cypher.execute("match (d:Date) where d.name='" + date + "' and d.parent='" + tag + "' create (n:News {name:'" + item + "'}), (d)-[:NEWS]->(n)")

fr.close()