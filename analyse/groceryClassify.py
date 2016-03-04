#!/usr/bin/env python
# coding:utf8
# 借助grocery包进行新闻分类

from tgrocery import Grocery
import random
# import matplotlib
# import matplotlib.pyplot as plt
# matplotlib.use('TkAgg')
# import pandas as pd
# import seaborn as sns
import sys 
reload(sys)
sys.setdefaultencoding('utf8')

grocery = Grocery('paris')

# 参考新闻的url和分类
inputFile = '../data/news_standard.txt'
fbase = open(inputFile, 'r')
# 待分类的数据
inputFile = '../data/news_ifeng.txt'
fsample = open(inputFile, 'r')
# 待分类数据的部分标签
inputFile = '../data/sampleTag.txt'
ftag = open(inputFile, 'r')
# outputFile = '../data/news_ifeng_classified_grocery.txt'
# fw = open(outputFile, 'w')

bases = []

print "分析参考新闻"
for line in fbase:
	line = line.rstrip('\n').split('^')
	# 参考新闻标签
	title = line[2]
	tag = line[4]
	if int(tag) == 1:
		tag = '新闻背景'
	elif int(tag) == 2:
		tag = '事实陈述'
	elif int(tag) == 3:
		tag = '事件演化'
	elif int(tag) == 4:
		tag = '各方态度'
	elif int(tag) == 6:
		tag = '直接关联'
	elif int(tag) == 7:
		tag = '暂无关联'

	# 记录term vector
	bases.append((tag, title))

sampleTag = {}
print "获取样本标签"
for line in ftag:
	line = line.rstrip('\n').split(',')
	news_id = line[0]
	error = line[1]
	tag = line[2]
	num = line[3]
	if int(tag) == 1:
		tag = '新闻背景'
	elif int(tag) == 2:
		tag = '事实陈述'
	elif int(tag) == 3:
		tag = '事件演化'
	elif int(tag) == 4:
		tag = '各方态度'
	elif int(tag) == 6:
		tag = '直接关联'
	elif int(tag) == 7:
		tag = '暂无关联'

	if float(error) == 0 and int(num) > 3:
		sampleTag[str(news_id)] = tag

print "分类样本新闻"
for line in fsample:
	line = line.rstrip('\n').split('^')
	news_id = line[0]
	title = line[1]
	# url = line[2]
	# date = line[3]
	# content = line[5]

	# 判断该新闻是否有学生标注
	if not sampleTag.has_key(str(news_id)):
		continue

	# 判断该新闻是否标题为空
	if title == '':
		continue

	# 记录term vector
	bases.append((sampleTag[str(news_id)], title))

result = {'true': 0, 'false': 0}
for n in xrange(0, len(bases)):
	test = bases[n]
	ans = {}
	for m in xrange(0, 1):
		tmp = []
		for x in xrange(0, len(bases)):
			if x == n:
				pass
				# continue
			if random.random() > 0:
				tmp.append(bases[x])

		grocery.train(tmp)
		grocery.save()
		new_grocery = Grocery('paris')
		new_grocery.load()
		tag = new_grocery.predict(test[1])
		
		if not ans.has_key(tag):
			ans[tag] = 1
		else:
			ans[tag] += 1

	ans = sorted(ans.iteritems(), key=lambda x:x[1], reverse=True)

	if ans[0][0] == test[0]:
		result['true'] += 1
	else:
		result['false'] += 1

print result['true'], result['false']
print float(result['true']) / float(result['true'] + result['false'])

# loop = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10]
# threshold = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
# score = [0.5862068965517241, 0.5747126436781609, 0.5517241379310345, 0.5057471264367817, 0.5057471264367817, 0.4425287356321839, 0.45977011494252873, 0.3735632183908046, 0.3275862068965517, 0.603448275862069, 0.5344827586206896, 0.5344827586206896, 0.5114942528735632, 0.47701149425287354, 0.47126436781609193, 0.43103448275862066, 0.367816091954023, 0.3275862068965517, 0.5689655172413793, 0.5574712643678161, 0.5344827586206896, 0.5632183908045977, 0.5459770114942529, 0.47701149425287354, 0.4540229885057471, 0.40229885057471265, 0.367816091954023, 0.5919540229885057, 0.5862068965517241, 0.5287356321839081, 0.5517241379310345, 0.47701149425287354, 0.5114942528735632, 0.47126436781609193, 0.41379310344827586, 0.39655172413793105, 0.5862068965517241, 0.5862068965517241, 0.5574712643678161, 0.5459770114942529, 0.5632183908045977, 0.5402298850574713, 0.4540229885057471, 0.4885057471264368, 0.3620689655172414, 0.5977011494252874, 0.5747126436781609, 0.5747126436781609, 0.5574712643678161, 0.5344827586206896, 0.5057471264367817, 0.4827586206896552, 0.4367816091954023, 0.3620689655172414, 0.5862068965517241, 0.5689655172413793, 0.5977011494252874, 0.5459770114942529, 0.5402298850574713, 0.5459770114942529, 0.4827586206896552, 0.45977011494252873, 0.3793103448275862, 0.5977011494252874, 0.603448275862069, 0.5747126436781609, 0.5402298850574713, 0.5402298850574713, 0.4942528735632184, 0.5057471264367817, 0.4367816091954023, 0.43103448275862066, 0.5919540229885057, 0.5919540229885057, 0.5862068965517241, 0.5402298850574713, 0.5344827586206896, 0.5114942528735632, 0.5114942528735632, 0.5287356321839081, 0.42528735632183906, 0.5862068965517241, 0.5919540229885057, 0.5689655172413793, 0.5977011494252874, 0.5919540229885057, 0.5517241379310345, 0.5114942528735632, 0.4540229885057471, 0.3850574712643678]
# 取loop为1，threshold为0，对应score为0.597701149425

# fw.write(str(news_id) + '^' + str(tag) + '^' + date + '^' + title + '^' + url + '^' + content + '\n')

fbase.close()
fsample.close()
ftag.close()
# fw.close()
