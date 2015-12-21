#!/usr/bin/env python
# coding:utf8
# 在每个标签下生成时间线并汇总

import math
import time
import jieba.analyse
import sys 
reload(sys)
sys.setdefaultencoding('utf8')

ISOTIMEFORMAT='%Y-%m-%d %X'

inputFile = '../data/news_ifeng_classified_grocery.txt'
fr = open(inputFile, 'r')
outputFile = '../data/timeline.txt'
fw = open(outputFile, 'w')

result = {}
titles = []

print '计算特征向量'
print time.strftime( ISOTIMEFORMAT, time.localtime() )
for line in fr:
	line = line.rstrip('\n').split('^')
	news_id = line[0]
	tag = line[1]
	timestamp = int(time.mktime(time.strptime(line[2], '%Y-%m-%d')))
	title = line[3]
	url = line[4]
	content = line[5]

	if title in titles:
		continue

	titles.append(title)

	if not result.has_key(tag):
		result[tag] = []

	# 使用标题提取TF
	words = jieba.analyse.extract_tags(title, topK=999, withWeight=True, allowPOS=())
	result[tag].append({'timestamp': timestamp, 'sentence': title, 'vector': words, 'rank': 1})

print '特征向量计算结束'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

# 余弦相似度计算
def cosine(s1, s2):
	inner = 0
	for i1 in s1:
		for i2 in s2:
			if i1[0] == i2[0]:
				inner += i1[1] * i2[1]

	norm1 = 0
	for i1 in s1:
		norm1 += i1[1] * i1[1]
	norm1 = math.sqrt(norm1)

	norm2 = 0
	for i2 in s2:
		norm2 += i2[1] * i2[1]
	norm2 = math.sqrt(norm2) 

	return float(inner) / float(norm1 * norm2 + 0.0000001)

def timeline(sentences, num):
	count = len(sentences)
	similarity = {}

	for x in xrange(0, count):
		similarity[str(x)] = {}
		for y in xrange(0, count):
			if x == y:
				continue
			elif x > y:
				similarity[str(x)][str(y)] = similarity[str(y)][str(x)]
			else:
				similarity[str(x)][str(y)] = cosine(sentences[x]['vector'], sentences[y]['vector']) * math.exp(-0.02*abs((sentences[x]['timestamp'] - sentences[y]['timestamp']) / 3600 / 24))

		total = 0
		for y in xrange(0, count):
			if y == x:
				continue
			total += similarity[str(x)][str(y)]
		similarity[str(x)]['total'] = total

	loop = 0
	while True:
		loop += 1
		print '第' + str(loop) + '轮迭代' 
		ranks = []
		for x in xrange(0, count):
			tmp = 0
			for y in xrange(0, count):
				if y == x:
					continue
				else:
					tmp += sentences[y]['rank'] * similarity[str(y)][str(x)] / (similarity[str(y)]['total'] + 0.0000001)
			ranks.append(tmp)

		totalChange = 0
		for x in xrange(0, count):
			totalChange += abs(ranks[x] - sentences[x]['rank'])

		for x in xrange(0, count):
			sentences[x]['rank'] = ranks[x]

		print totalChange
		if totalChange < 0.0001:
			break

	sentences.sort(lambda x, y:cmp(x['rank'], y['rank']), reverse=True)

	sentences = sentences[0:num]

	sentences.sort(lambda x, y:cmp(x['timestamp'], y['timestamp']), reverse=True)

	for item in sentences:
		item['timestamp'] = time.strftime('%Y-%m-%d', time.localtime(item['timestamp']))

	return sentences

for key, value in result.items():
	print key
	fw.write(key + '\n')
	records = timeline(value, 50)
	for item in records:
		print item['timestamp'], item['sentence']
		fw.write(item['timestamp'] + '^' + item['sentence'] + '\n')
	fw.write('\n')

fr.close()
fw.close()