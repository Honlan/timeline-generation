#!/usr/bin/env python
# coding:utf8
# 获取参考新闻的标题和内容，并以此为基准进行新闻分类

import math
import jieba.analyse
import sys 
reload(sys)
sys.setdefaultencoding('utf8')

# 参考新闻的url和分类
inputFile = '../data/news_standard.txt'
fbase = open(inputFile, 'r')
# 待分类的数据
inputFile = '../data/news_ifeng.txt'
fsample = open(inputFile, 'r')
# 待分类数据的部分标签
inputFile = '../data/sampleTag.txt'
ftag = open(inputFile, 'r')
outputFile = '../data/news_ifeng_classified_cos.txt'
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

sampleTag = {}
print "获取学生对样本新闻所打标签"
for line in ftag:
	line = line.rstrip('\n').split(',')
	news_id = line[0]
	error = line[1]
	tag = line[2]
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
	sampleTag[str(news_id)] = {'error':error, 'tag':tag}

tagStat = {}
correct = {'true':0, 'false':0}
print "分类样本新闻"
for line in fsample:
	line = line.rstrip('\n').split('^')
	news_id = line[0]
	title = line[1]
	url = line[2]
	date = line[3]
	content = line[5]

	# 判断该新闻是否有学生标注
	if not sampleTag.has_key(str(news_id)):
		continue

	# 判断该新闻是否标题为空
	if title == '':
		continue

	# 将标题和内容组合成待分析文本
	content = title * alpha + content
	content = jieba.analyse.textrank(content, topK=9999, withWeight=True, allowPOS=('nr','ns','nt','n','vn','v')) 

	# 记录term vector
	tmp = {}
	for item in content:
		tmp[item[0]] = item[1]

	content = line[5]

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
	errors = sorted(errors.iteritems(), key=lambda x:x[1]['average'])

	# print title
	# for item in errors:
	# 	print item[0], item[1]

	# 统计各个标签出现次数
	if not tagStat.has_key(errors[0][0]):
		tagStat[errors[0][0]] = 1
	else:
		tagStat[errors[0][0]] += 1
	# 统计分类正确和错误的数量
	if errors[0][0] == sampleTag[str(news_id)]['tag']:
		correct['true'] += 1
	else:
		correct['false'] += 1

	# 将正确分类且方差小的样本加入基准集
	if float(sampleTag[str(news_id)]['error']) == 0:
		bases.append({'vector': tmp, 'tag': sampleTag[str(news_id)]['tag']})
		print "添加一条基准数据"

	fw.write(str(news_id) + '^' + errors[0][0] + '^' + date + '^' + title + '^' + url + '^' + content + '\n')

for key, value in tagStat.items():
	print key, value

print 'true ' + str(correct['true']) 
print 'false ' + str(correct['false'])
print 'rate ' + str(float(correct['true']) / float(correct['true'] + correct['false']))

fbase.close()
fsample.close()
ftag.close()
fw.close()
