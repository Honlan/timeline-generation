#!/usr/bin/env python
# coding:utf8
# 获取参考新闻的标题和内容，并以此为基准进行新闻分类

import time
import math
import jieba.analyse
import sys 
reload(sys)
sys.setdefaultencoding('utf8')

inputFile = '../data/news_standard.txt'
# 参考新闻的url和分类
fbase = open(inputFile, 'r')
inputFile = '../data/news_ifeng.txt'
# 待分类的数据
fsample = open(inputFile, 'r')
outputFile = '../data/news_ifeng_classified.txt'
fw = open(outputFile, 'w')

bases = []
# 标题和正文权重比
alpha = 10

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

print "分析参考新闻"
for line in fbase:
	line = line.rstrip('\n').split('^')
	# 参考新闻标签
	title = line[2]
	tag = line[4]
	content = line[5]
	if int(tag) == 1:
		tag = '新闻背景'
	elif int(tag) == 2:
		tag = '事实陈述'
	elif int(tag) == 3:
		tag = '各方态度'
	elif int(tag) == 4:
		tag = '事件演化'
	elif int(tag) == 6:
		tag = '直接关联'
	elif int(tag) == 7:
		tag = '暂无关联'
	# 将标题和内容组合成待分析文本
	content = title * alpha + content
	content = jieba.analyse.textrank(content, topK=9999, withWeight=True, allowPOS=('nr','ns','nt','n','vn','v')) 

	# 记录term vector
	tmp = {}
	for item in content:
		tmp[item[0]] = item[1]
	bases.append({'vector': tmp, 'tag': tag})


tagStat = {}
print "分类样本新闻"
for line in fsample:
	line = line.rstrip('\n').split('^')
	title = line[1]
	url = line[2]
	content = line[5]
	# 将标题和内容组合成待分析文本
	content = title * alpha + content
	content = jieba.analyse.textrank(content, topK=9999, withWeight=True, allowPOS=('nr','ns','nt','n','vn','v')) 

	# 记录term vector
	tmp = {}
	for item in content:
		tmp[item[0]] = item[1]

	# 比较term vector
	errors = {}
	for item in bases:
		vector = item['vector']
		tag = item['tag']
		e = cosine(tmp, vector)
		if not errors.has_key(tag):
			errors[tag] = {'average': e, 'count': 1}
		else:
			count = errors[tag]['count']
			average = errors[tag]['average']
			errors[tag]['average'] = (average * count + e) / (count + 1)
			errors[tag]['count'] = count + 1

	# 根据误差大小排序
	errors = sorted(errors.iteritems(), key=lambda x:x[1])

	print title
	for item in errors:
		print item[0], item[1]

	# 统计各个标签出现次数
	if not tagStat.has_key(errors[0][0]):
		tagStat[errors[0][0]] = 1
	else:
		tagStat[errors[0][0]] += 1

	fw.write(errors[0][0] + '^' + title + '^' + url + '\n')

for key, value in tagStat.items():
	print key, value

fbase.close()
fsample.close()
fw.close()
