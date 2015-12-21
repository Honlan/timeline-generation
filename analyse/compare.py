#!/usr/bin/env python
# coding:utf-8
# 比较并生成时间线

import time
import math
import jieba.posseg as pseg 

inputFile = "../data/news_new.txt"
fr = open(inputFile, 'r')
outputFile = "../data/summary.txt"
fw = open(outputFile, 'w')

sentences = {}

ISOTIMEFORMAT='%Y-%m-%d %X'

print '分词开始'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

count = 0
scount = 0

for line in fr:
	line = line.strip('\n').split('^')
	timestamp = line[4]
	abstract = line[5]
	content = line[6]

	if abstract == '':
		continue

	if not (timestamp[0:4] == '2015'):
		continue

	timestamp = int(time.mktime(time.strptime(timestamp, '%Y年%m月%d日 %H:%M')))

	# content = content.replace('。', '\\\\')
	# abstract = content.split('\\\\')

	abstract = abstract.split('。')

	senCount = 0
	senStat = {}

	for item in abstract:
		if len(item) <= 10:
			continue

		senList = []

		count += 1

		senCount += 1

		sentences[str(count)] = {}
		sentences[str(count)]['timestamp'] = timestamp
		sentences[str(count)]['sentence'] = item

		words = pseg.cut(item)
		TF = {}
		for word, flag in words:
			if word == '':
				continue

			if flag == 'x':
				continue

			if not TF.has_key(word):
				TF[word] = 1
			else:
				TF[word] += 1

			if not senStat.has_key(word):
				senStat[word] = 1
				senList.append(word)
			elif word not in senList:
				senStat[word] += 1

		sentences[str(count)]['vector'] = TF
		sentences[str(count)]['rank'] = 1

	while scount < count:
		scount += 1
		for k, v in sentences[str(scount)]['vector'].items():
			v *= math.log(float(senCount) / float(senStat[k]))

print str(count) + '条语句'

print '分词结束'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

print '计算相似度开始'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

def cosine(index1, index2):
	s1 = sentences[str(index1)]
	s2 = sentences[str(index2)]
	inner = 0
	for k1, v1 in s1['vector'].items():
		for k2, v2 in s2['vector'].items():
			if k1 == k2:
				inner += v1 * v2

	norm1 = 0
	for k1, v1 in s1['vector'].items():
		norm1 += v1 * v1
	norm1 = math.sqrt(norm1)

	norm2 = 0
	for k2, v2 in s2['vector'].items():
		norm2 += v2 * v2
	norm2 = math.sqrt(norm2)

	return float(inner) / float(norm1 * norm2 + 0.0000001)

similarity = {}
threshold = 0.01
alpha = 5
for x in xrange(1, count + 1):
	print '计算' + str(x) + '的相似度'
	similarity[str(x)] = {}
	for y in xrange(1, count + 1):
		if y == x:
			continue
		elif y < x:
			similarity[str(x)][str(y)] = similarity[str(y)][str(x)]
		else:
			similarity[str(x)][str(y)] = cosine(x, y) * alpha * math.exp(-abs((sentences[str(y)]['timestamp'] - sentences[str(x)]['timestamp']) / 3600 / 24))

	total = 0
	for y in xrange(1, count + 1):
		if y == x:
			continue
		else:
			total += similarity[str(x)][str(y)]

	similarity[str(x)]['total'] = total

print '计算相似度结束'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

print '迭代开始'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

loop = 0

errors = {}

lastChange = 0.1

while True:
	loop += 1
	print '第' + str(loop) + '轮迭代'
	totalChange = 0
	temp = {}

	for x in xrange(1, count + 1):
		total = 0
		for y in xrange(1, count + 1):
			if y == x:
				continue
			else:
				total += sentences[str(y)]['rank'] * similarity[str(y)][str(x)] / (similarity[str(y)]['total'] + 0.0000001)
		temp[str(x)] = total

	for x in xrange(1, count + 1):
		totalChange += abs(sentences[str(x)]['rank'] - temp[str(x)])

	for x in xrange(1, count + 1):
		sentences[str(x)]['rank'] = temp[str(x)]

	errors[str(loop)] = totalChange

	print totalChange

	if totalChange / lastChange < 0.01 or loop == 20:
		break

	lastChange = totalChange

print '迭代结束'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

print '输出rank最高的50条语句'
sentences = sorted(sentences.iteritems(), key=lambda x:x[1]['rank'], reverse=True)

for item in sentences:
	fw.write(str(item[1]['timestamp']) + '^' + item[1]['sentence'] + '^' + str(item[1]['rank']) + '\n')

errors = sorted(errors.iteritems(), key=lambda x:int(x[0]))
temp = ''
for item in errors:
	temp += str(item[0]) + ':' + str(item[1]) + ' '

print temp[:-1]

fr.close()
fw.close()