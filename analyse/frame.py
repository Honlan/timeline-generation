#!/usr/bin/env python
# coding:utf8
# 分类第一步，直接关联和暂无关联

import jieba.analyse
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import math
import sys 
reload(sys)
sys.setdefaultencoding('utf8')
import random
import time
print 'load model'
import gensim
model = gensim.models.Word2Vec.load("../data/wiki.zh.text.model")
print 'load finish'

# 参考新闻的url和分类
inputFile = '../data/trainset.txt'
fr = open(inputFile, 'r')

jieba.enable_parallel(5)

print '获取文本数据'
news = []
titles = []
corpus = ''
# 标题和正文权重比
alpha = 1
beta = 1
for line in fr:
	line = line.rstrip('\n').split('^')
	news_id = int(line[0])
	url = line[1]
	title = line[2]
	timestamp = int(time.mktime(time.strptime(line[3], '%Y-%m-%d')))
	tag = int(line[4])
	content = line[5]

	if title in titles:
		continue

	print title
	titles.append(title)

	if tag == 7:
		tag = 0
	else:
		tag = 1

	content = title * alpha + content * beta
	corpus += content
	
	content = jieba.analyse.textrank(content, topK=100, withWeight=True, allowPOS=('nr','ns','nt','nz','n','vn','v')) 

	news.append({'title': title, 'timestamp': timestamp, 'vector': content, 'tag': tag, 'label': 0})

print '共' + str(len(news)) + '条数据'

# 计算余弦距离
def cosine(s1, s2):
	inner = 0
	count = 0
	if len(s1) > len(s2):
		length = len(s2)
	else:
		length = len(s1)
	for x in xrange(0, length):
		try:
			inner += s1[x][1] * s2[x][1] * abs(model.similarity(s1[x][0].decode('utf8'), s2[x][0].decode('utf8')))
		except Exception, e:
			if s1[x][0] == s2[x][0]:
				inner += s1[x][1] * s2[x][1]
		else:
			pass
		finally:
			count += s1[x][1] * s2[x][1]

	if count == 0:
		result = 0
	else:
		result = float(inner) / float(count)

	return result 

def mapping(li, order):
	tmp = []
	for item in li:
		tmp.append(math.pow(item, order))

	maxv = np.max([x for x in tmp])
	minv = np.min([x for x in tmp])
	return [(x - minv) / (maxv - minv) for x in tmp]

def decay(li, order):
	return [math.exp(-order*x) for x in li]

corpus = jieba.analyse.textrank(corpus, topK=100, withWeight=True, allowPOS=('nr','ns','nt','nz','n','vn','v')) 

timestd = np.std([x['timestamp'] for x in news])
textual = []
temporal = []

for x in xrange(0, len(news)):
	timedecay = 0
	for y in xrange(0, len(news)):
		if x == y:
			continue
		timedecay += abs(news[x]['timestamp'] - news[y]['timestamp'])
	timedecay = float(timedecay) / len(news)
	textual.append(cosine(news[x]['vector'], corpus))
	temporal.append(timedecay / timestd)

# x = 1
# y = 5
for x in xrange(1, 10):
	for y in xrange(1, 10):
		tmp_text = mapping(textual, x)
		tmp_temp = decay(temporal, y)

		for z in xrange(0, len(news)):
			news[z]['label'] = tmp_text[z] * tmp_temp[z]

		maxv = np.max([z['label'] for z in news])
		minv = np.min([z['label'] for z in news])

		for z in xrange(0, len(news)):
			news[z]['label'] = (news[z]['label'] - minv) / (maxv - minv)

		# X = []
		# Y = []
		# for z in xrange(0, len(news)):
		# 	X.append(news[z]['label'])
		# 	Y.append(float(news[z]['tag']) + random.random() * 0.4 - 0.2)
		# sns.jointplot(x='label', y='tag', data=pd.DataFrame({'label': X, 'tag': Y}), kind='scatter')
		# plt.title('textual order ' + str(x) + ', temporal order ' + str(y))
		# plt.show()

		true = 0
		false = 0
		for z in xrange(0, len(news)):
			if news[z]['label'] < 0.04 and news[z]['tag'] == 0:
				true += 1
			elif news[z]['label'] >= 0.04 and news[z]['tag'] == 1:
				true += 1
			else:
				false += 1
		print 'textual decay ' + str(x) + ', temporal decay ' + str(y) + ', accuracy ' + str(float(true) / (float(true) + float(false)))

fr.close()