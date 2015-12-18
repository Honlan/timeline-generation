#!/usr/bin/env python
# coding:utf-8
# 分别计算每天有多少条原始数据和去重数据

import time

inputFile = '../data/news.txt'
fr1 = open(inputFile, 'r')
inputFile = '../data/news_unique.txt'
fr2 = open(inputFile, 'r')

ISOTIMEFORMAT='%Y-%m-%d %X'

print '统计开始'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

result = {}

for line in fr1:
	line = line.split('^')
	timestamp = line[4]

	if not (timestamp[0:4] == '2015'):
		continue
	
	timestamp = timestamp[0:timestamp.find(' ')]
	timestamp = timestamp[7:]
	timestamp = timestamp.replace('月', '-')
	timestamp = timestamp.replace('日', '')
	
	if not result.has_key(timestamp):
		result[timestamp] = 1
	else:
		result[timestamp] = result[timestamp] + 1

result = sorted(result.iteritems(), key=lambda x:x[0])

count = 0
day = ''
data = ''
for item in result:
	count = count + item[1]
	day += "'" + item[0] + "',"
	data += "'" + str(item[1]) + "',"
print day[0:-1]
print data[0:-1]
print '原始数据共' + str(count) + '条'

result = {}

for line in fr2:
	line = line.split('^')
	timestamp = line[4]

	if not (timestamp[0:4] == '2015'):
		continue
	
	timestamp = timestamp[0:timestamp.find(' ')]
	timestamp = timestamp[7:]
	timestamp = timestamp.replace('月', '-')
	timestamp = timestamp.replace('日', '')
	
	if not result.has_key(timestamp):
		result[timestamp] = 1
	else:
		result[timestamp] = result[timestamp] + 1

result = sorted(result.iteritems(), key=lambda x:x[0])

count = 0
day = ''
data = ''
for item in result:
	count = count + item[1]
	day += "'" + item[0] + "',"
	data += "'" + str(item[1]) + "',"
print day[0:-1]
print data[0:-1]
print '去重数据共' + str(count) + '条'

print '统计结束'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

fr1.close()
fr2.close()