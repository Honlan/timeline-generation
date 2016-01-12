#!/usr/bin/env python
# coding:utf8
# 使用lda进行聚类

import jieba
import jieba.posseg as pseg
import time
import numpy as np
import lda
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
import pandas as pd
import seaborn as sns
import random
import sys 
reload(sys)
sys.setdefaultencoding('utf8')

ISOTIMEFORMAT='%Y-%m-%d %X'

# 参考新闻的url和分类
inputFile = '../data/news_standard.txt'
fbase = open(inputFile, 'r')
# 待分类的数据
inputFile = '../data/news_ifeng.txt'
fsample = open(inputFile, 'r')
# 待分类数据的部分标签
inputFile = '../data/sampleTag.txt'
ftag = open(inputFile, 'r')
# outputFile = '../data/news_ifeng_cluster.txt'
# fw = open(outputFile, 'w')

jieba.enable_parallel(10)

# 标题和正文权重比
alpha = 10

news = {}

corpus = []
matrix = []
titles = []

tagStat = {}
print "分析参考新闻"
for line in fbase:
	line = line.rstrip('\n').split('^')
	# 参考新闻标签
	title = line[2]
	tag = line[4]
	content = line[5]

	tmp = {}
	words = pseg.cut(title * alpha + content)
	for word, flag in words:
		if flag == 'x':
			continue

		if not tmp.has_key(word):
			tmp[word] = 0
		tmp[word] += 1

		if not word in corpus:
			corpus.append(word)

	news[title] = tmp
	tagStat[title] = tag

tagSample = {}
print "获取样本标签"
for line in ftag:
	line = line.rstrip('\n').split(',')
	news_id = line[0]
	error = line[1]
	tag = line[2]
	num = line[3]

	if float(error) == 0 and int(num) > 1:
		tagSample[str(news_id)] = int(tag)

print "处理样本新闻"
for line in fsample:
	line = line.rstrip('\n').split('^')
	news_id = line[0]
	title = line[1]
	url = line[2]
	date = line[3]
	content = line[5]

	# 判断该新闻是否有学生标注
	if not tagSample.has_key(str(news_id)):
		continue

	# 判断该新闻是否标题为空
	if title == '':
		continue

	tmp = {}
	words = pseg.cut(title * alpha + content)
	for word, flag in words:
		if flag == 'x':
			continue

		if not tmp.has_key(word):
			tmp[word] = 0
		tmp[word] += 1

		if not word in corpus:
			corpus.append(word)

	news[title] = tmp
	tagStat[title] = tagSample[str(news_id)]

print "计算关联矩阵"
for key, value in news.items():
	titles.append(key)
	tmp = []
	for item in corpus:
		if not value.has_key(item):
			tmp.append(0)
		else:
			tmp.append(value[item])
	matrix.append(tmp)
matrix = np.array(matrix)
print matrix.shape, len(titles), len(corpus)

model = lda.LDA(n_topics=6, n_iter=100, random_state=1)
model.fit(matrix)

topic_word = model.topic_word_
print "输出每个topic的前20个关键词"
n = 20
for i, topic_dist in enumerate(topic_word):
    topic_words = np.array(corpus)[np.argsort(topic_dist)][:-(n+1):-1]
    print('* Topic: {}\n- {}'.format(i, ' '.join(topic_words)))

# print "输出每篇文章的topic概率分布"
doc_topic = model.doc_topic_
# for n in xrange(0, len(titles)):
#     topic_most_pr = doc_topic[n].argmax()
#     print("* Doc: {} Topic: {} Tag: {}\n- {}".format(n, topic_most_pr, tagStat[titles[n]], titles[n]))

result = {'topic': [], 'tag': []}
for n in xrange(0, len(titles)):
    topic_most_pr = doc_topic[n].argmax()
    result['topic'].append(float(topic_most_pr) + (random.random() * 0.4 - 0.2))
    result['tag'].append(float(tagStat[titles[n]]) + (random.random() * 0.4 - 0.2))
result = pd.DataFrame(result)
sns.jointplot(x='topic', y='tag', data=result)
# sns.kdeplot(result['topic'], result['tag'], shade=True)
plt.title('新闻分类事件聚类结果')
plt.show()

fbase.close()
fsample.close()
ftag.close()
# fw.close()