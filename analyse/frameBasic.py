#!/usr/bin/env python
# coding:utf8
# 分类第一步，直接关联和暂无关联

import jieba.analyse
import jieba.posseg as pseg
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import lda
import math
import sys 
reload(sys)
sys.setdefaultencoding('utf8')
import random

# 参考新闻的url和分类
inputFile = '../data/trainset.txt'
# inputFile = '../data/news_standard.txt'
fr = open(inputFile, 'r')

jieba.enable_parallel(10)

print '获取文本数据'
news = []
corpus = []
minmin = 999
# 标题和正文权重比
alpha = 1
beta = 1
for line in fr:
	line = line.rstrip('\n').split('^')
	news_id = int(line[0])
	url = line[1]
	title = line[2]
	timestamp = line[3]
	tag = int(line[4])
	content = line[5]

	if tag == 7:
		tag = 0
	else:
		tag = 1

	content = title * alpha + content * beta
	
	content = jieba.analyse.textrank(content, topK=20, withWeight=True, allowPOS=('nr','ns','nt','nz','n','vn','v')) 
	# content = jieba.analyse.extract_tags(content, topK=999, withWeight=True, allowPOS=('ns', 'n', 'vn', 'n')) 
	print content[0][0], content[1][0], content[2][0]
	tmp = {}
	for item in content:
		tmp[item[0]] = item[1]
		if not item[0] in corpus:
			corpus.append(item[0])
		if item[1] < minmin:
			minmin = item[1]

	# content = pseg.cut(content)
	# tmp = {}
	# for word, flag in content:
	# 	if flag == 'x':
	# 		continue
	# 	if not tmp.has_key(word):
	# 		tmp[word] = 0
	# 	tmp[word] += 1

	news.append({'title': title, 'vector': tmp, 'news_id': news_id, 'tag': tag, 'label': 0})

print '共' + str(len(news)) + '条数据，语料包含词语' + str(len(corpus)) + '个'
minmin = math.ceil(1 / minmin)

# ************************************************************************************
print '基于余弦相似度'

# 余弦相似度计算
def cosine(s1, s2):
	inner = 0
	for k1, v1 in s1.items():
		for k2, v2 in s2.items():
			if k1 == k2:
				inner += v1 * v2

	norm1 = 0
	for k1, v1 in s1.items():
		norm1 += v1 * v1
	norm1 = math.sqrt(norm1)

	norm2 = 0
	for k2, v2 in s2.items():
		norm2 += v2 * v2
	norm2 = math.sqrt(norm2)

	return math.acos(float(inner) / float(norm1 * norm2 + 0.0000001))

similarity = {}
for x in xrange(0, len(news)):
	similarity[str(x)] = {}
	for y in xrange(0, len(news)):
		if y == x:
			continue
		elif y < x:
			similarity[str(x)][str(y)] = similarity[str(y)][str(x)]
		else:
			similarity[str(x)][str(y)] = cosine(news[x]['vector'], news[y]['vector'])

	total = 0
	for y in xrange(0, len(news)):
		if y == x:
			continue
		else:
			total += similarity[str(x)][str(y)]
	news[x]['label'] = float(total) / len(news)

X = []
Y = []
for x in xrange(0, len(news)):
	X.append(news[x]['label'])
	Y.append(float(news[x]['tag']) + random.random() * 0.4 - 0.2)
sns.jointplot(x='label', y='tag', data=pd.DataFrame({'label': X, 'tag': Y}), kind='scatter')
plt.title('Cosine')
plt.show()

# 基于余弦相似度
# ************************************************************************************

# ************************************************************************************
print '基于kmean'

data = []
tags = []
for item in news:
	tmp = []
	for i in corpus:
		if not item['vector'].has_key(i):
			tmp.append(0)
		else:
			tmp.append(item['vector'][i])
	data.append(tmp)
	tags.append(float(item['tag']) + random.random() * 0.4 - 0.2)

kmeans = KMeans(init='k-means++', n_clusters=2, n_init=20)
labels = kmeans.fit_predict(data)
tmp = []
for l in labels:
	tmp.append(l + random.random() * 0.4 - 0.2)
labels = tmp
# for x in xrange(0, len(labels)):
# 	if round(labels[x]) == round(tags[x]):
# 		print news[x]['title']
sns.jointplot(x='label', y='tag', data=pd.DataFrame({'label': labels, 'tag': tags}))
plt.title('KMEANS')
plt.show()

# 基于kmean
# ************************************************************************************

# ************************************************************************************
print '基于lda'

matrix = []
tags = []
for item in news:
	tmp = []
	for i in corpus:
		if not item['vector'].has_key(i):
			tmp.append(0)
		else:
			tmp.append(int(math.ceil(minmin * item['vector'][i])))
	matrix.append(tmp)
	tags.append(float(item['tag']) + random.random() * 0.4 - 0.2)
matrix = np.array(matrix)
model = lda.LDA(n_topics=2, n_iter=100, random_state=1)
model.fit(matrix)

# topic_word = model.topic_word_
# print "输出每个topic的前20个关键词"
# n = 20
# for i, topic_dist in enumerate(topic_word):
#     topic_words = np.array(corpus)[np.argsort(topic_dist)][:-(n+1):-1]
#     print('* Topic: {}\n- {}'.format(i, ' '.join(topic_words)))

# print "输出每篇文章的topic概率分布"
doc_topic = model.doc_topic_
# for n in xrange(0, len(titles)):
#     topic_most_pr = doc_topic[n].argmax()
#     print("* Doc: {} Topic: {} Tag: {}\n- {}".format(n, topic_most_pr, tagStat[titles[n]], titles[n]))

topics = []
for n in xrange(0, len(tags)):
    topic_most_pr = doc_topic[n].argmax()
    topics.append(float(topic_most_pr) + (random.random() * 0.4 - 0.2))
# for x in xrange(0, len(topics)):
# 	if round(topics[x]) == round(tags[x]):
# 		print news[x]['title']
sns.jointplot(x='topic', y='tag', data=pd.DataFrame({'topic': topics, 'tag': tags}))
plt.title('LDA')
plt.show()

# 基于lda
# ************************************************************************************

# ************************************************************************************
print '基于欧式距离'

# 余弦相似度计算
def distance(s1, s2):
	total = 0
	for x in xrange(0, len(s1)):
		total += (s1[x] - s2[x]) * (s1[x] - s2[x])
	return math.sqrt(total)

data = []
tags = []
dists = []
for item in news:
	tmp = []
	for i in corpus:
		if not item['vector'].has_key(i):
			tmp.append(0)
		else:
			tmp.append(item['vector'][i])
	data.append(tmp)
	tags.append(float(item['tag']) + random.random() * 0.4 - 0.2)

distances = {}
for x in xrange(0, len(news)):
	distances[str(x)] = {}
	for y in xrange(0, len(news)):
		if y == x:
			continue
		elif y < x:
			distances[str(x)][str(y)] = distances[str(y)][str(x)]
		else:
			distances[str(x)][str(y)] = distance(data[x], data[y])

	total = 0
	for y in xrange(0, len(news)):
		if y == x:
			continue
		else:
			total += distances[str(x)][str(y)]
	dists.append(float(total) / len(news))

sns.jointplot(x='distance', y='tag', data=pd.DataFrame({'distance': dists, 'tag': tags}))
plt.title('Distance')
plt.show()

# 基于欧式距离
# ************************************************************************************

fr.close()