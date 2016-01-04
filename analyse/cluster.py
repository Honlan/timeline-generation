#!/usr/bin/env python
# coding:utf8
# 测试词性

import jieba.analyse
import jieba.posseg as pseg
import time
from sklearn.cluster import KMeans
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
import pandas as pd
import seaborn as sns
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

corpus = []
alpha = 10

news = {}

count = 0

tmp = {'id': [], 'tag': []}
tagIds = []
print "获取学生对样本新闻所打标签"
print time.strftime( ISOTIMEFORMAT, time.localtime() )
for line in ftag:
	line = line.rstrip('\n').split(',')
	news_id = line[0]
	error = line[1]
	tag = line[2]
	# if int(tag) == 1:
	# 	tag = '新闻背景'
	# elif int(tag) == 2:
	# 	tag = '事实陈述'
	# elif int(tag) == 3:
	# 	tag = '各方态度'
	# elif int(tag) == 4:
	# 	tag = '事件演化'
	# elif int(tag) == 6:
	# 	tag = '直接关联'
	# elif int(tag) == 7:
	# 	tag = '暂无关联'
	tmp['id'].append(int(news_id))
	tmp['tag'].append(int(tag))
	tagIds.append(news_id)

print '学生标注共' + str(len(tagIds)) + '条'
tmp = pd.DataFrame(tmp)
sns.jointplot(x='id', y='tag', data=tmp)
plt.title('新闻分类学生标注结果')
plt.figure(1)

print '遍历所有新闻'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

for line in fsample:
	count += 1
	print count

	line = line.rstrip('\n').split('^')
	news_id = line[0]
	title = line[1]
	url = line[2]
	timestamp = int(time.mktime(time.strptime(line[3], '%Y-%m-%d')))
	cover = line[4]
	content = line[5]

	if not news_id in tagIds:
		continue

	# 基于词分布
	'''
	content = jieba.analyse.extract_tags(content, topK=30, withWeight=True, allowPOS=('nr','ns','nt','n','vn','v'))
	tmp = {}
	for item in content:
		if item[0] not in corpus:
			corpus.append(item[0])

		tmp[item[0]] = float('%.4f' % item[1])
	'''

	# 基于词性分布
	# '''
	content = pseg.cut(content)
	tmp = {}
	for word, flag in content:
		if flag == 'x':
			continue
		if flag not in corpus:
			corpus.append(flag)

		if not tmp.has_key(flag):
			tmp[flag] = 0
		tmp[flag] += 1
	# '''
	
	if not news.has_key(str(news_id)):
		news[str(news_id)] = tmp

	# if count == 10:
	# 	break

print '生成特征向量'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

data = []
ids = []

for key, value in news.items():
	tmp = []
	for item in corpus:
		if not value.has_key(item):
			tmp.append(0)
		else:
			tmp.append(value[item])
	data.append(tmp)
	ids.append(int(key))

maxN = []

for x in xrange(0, len(data[0])):
	tmp = -1
	for y in xrange(0, len(data)):
		if data[y][x] > tmp:
			tmp = data[y][x]
	maxN.append(tmp)

for x in xrange(0, len(data)):
	for y in xrange(0, len(data[0])):
		data[x][y] = float('%.4f' % (float(data[x][y]) / float(maxN[y])))

kmeans = KMeans(init='k-means++', n_clusters=6, n_init=10)
labels = kmeans.fit_predict(data)
print '分类结果共' + str(len(labels)) + '条'

result = {'id': [], 'label': []}
for x in xrange(0, len(labels)):
	result['id'].append(ids[x])
	result['label'].append(labels[x])
result = pd.DataFrame(result)
sns.jointplot(x='id', y='label', data=result)
plt.title('新闻分类事件聚类结果')
plt.show()

fbase.close()
fsample.close()
ftag.close()
# fw.close()