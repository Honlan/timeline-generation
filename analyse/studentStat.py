#!/usr/bin/env python
# coding:utf8
# 评估学生标注的质量情况

import time
import math
import sys 
reload(sys)
sys.setdefaultencoding('utf8')

inputFile = '../data/action.txt'
fr = open(inputFile, 'r')
outputFile = '../data/sampleTag.txt'
fw = open(outputFile, 'w')

def cov(news):
	average = [0,0,0,0,0,0]
	count = len(news)
	for item in news:
		for x in xrange(0, 6):
			average[x] += item[x]

	for x in xrange(0,6):
		average[x] = float(average[x]) / float(count)

	total = 0
	for item in news:
		tmp = 0
		for x in xrange(0, 6):
			tmp += (item[x] - average[x]) * (item[x] - average[x])
		tmp = math.sqrt(tmp)
		total += tmp
	total /= count

	tag = [1,2,3,4,6,7]

	return [float('%.3f' % total), tag[average.index(max(average))], count] 

# 记录各个新闻的标注结果
stat = {}
result = {}

# fw.write('id^error^tag^num\n')

for line in fr:
	line = line.rstrip('\n').split('^')
	student_id = line[1]
	news_id = line[2]
	tag = line[3]

	if not stat.has_key(str(news_id)):
		stat[str(news_id)] = []

	if tag == '1':
		stat[str(news_id)].append([1,0,0,0,0,0])
	elif tag == '2':
		stat[str(news_id)].append([0,1,0,0,0,0])
	elif tag == '3':
		stat[str(news_id)].append([0,0,1,0,0,0])
	elif tag == '4':
		stat[str(news_id)].append([0,0,0,1,0,0])
	elif tag == '6':
		stat[str(news_id)].append([0,0,0,0,1,0])
	elif tag == '7':
		stat[str(news_id)].append([0,0,0,0,0,1])

# 计算各条新闻的方差
for key, value in stat.items():
	result[key] = cov(value)

result = sorted(result.iteritems(), key=lambda x:float(x[1][0]))

echo = '['
count = 0
for item in result:
	print item[0], item[1]
	echo += '[' + str(count) + ',' + str(item[1][0]) + '],'
	count += 1
	fw.write(str(item[0]) + ',' + str(item[1][0]) + ',' + str(item[1][1]) + ',' + str(item[1][2]) + '\n')
print echo[:-1] + ']'

fr.close()
fw.close()