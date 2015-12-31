#!/usr/bin/env python
# coding:utf8
# 借助grocery包进行新闻分类

from tgrocery import Grocery
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
import pandas as pd
import seaborn as sns
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
outputFile = '../data/news_ifeng_classified_grocery.txt'
fw = open(outputFile, 'w')

bases = []
# 标题和正文权重比
alpha = 10

print "分析参考新闻"
for line in fbase:
	line = line.rstrip('\n').split('^')
	# 参考新闻标签
	title = line[2]
	tag = line[4]
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

	# 记录term vector
	bases.append((int(tag), title))

sampleTag = {}
print "获取学生对样本新闻所打标签"
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

	sampleTag[str(news_id)] = {'error':error, 'tag':int(tag)}

# 一次性增强训练集
'''
print "一次性增强训练集"
for line in fsample:
	line = line.rstrip('\n').split('^')
	news_id = line[0]
	title = line[1]
	if sampleTag.has_key(str(news_id)) and float(sampleTag[str(news_id)]['error']) == 0:
		bases.append((sampleTag[str(news_id)]['tag'], title))
print len(bases)
fsample.close()
inputFile = '../data/news_ifeng.txt'
fsample = open(inputFile, 'r')
'''

grocery.train(bases)
grocery.save()
new_grocery = Grocery('paris')
new_grocery.load()

tagStat = {}
correct = {'true':0, 'false':0}
ids = []
labels = []
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

	# 只分类零误差标注且不在训练集中的新闻
	# if not float(sampleTag[str(news_id)]['error']) == 0:
	# 	continue

	tag = new_grocery.predict(title)

	# 统计各个标签出现次数
	if not tagStat.has_key(tag):
		tagStat[tag] = 1
	else:
		tagStat[tag] += 1
	# 统计分类正确和错误的数量
	if tag == sampleTag[str(news_id)]['tag']:
		correct['true'] += 1
	else:
		correct['false'] += 1

	# 渐进式增强训练集
	# '''
	# 将方差为零的样本加入基准集
	if float(sampleTag[str(news_id)]['error']) == 0:
	# if True:
		bases.append((sampleTag[str(news_id)]['tag'], title))
		print "添加一条基准数据"
		grocery.train(bases)
		grocery.save()
		new_grocery = Grocery('paris')
		new_grocery.load()
	# '''

	fw.write(str(news_id) + '^' + str(tag) + '^' + date + '^' + title + '^' + url + '^' + content + '\n')

	ids.append(int(news_id))
	labels.append(int(tag))

sns.jointplot(x='id', y='label', data=pd.DataFrame({'id':ids, 'label':labels}))
plt.title('新闻分类事件分类结果')
plt.show()

for key, value in tagStat.items():
	print key, value

print 'true ' + str(correct['true']) 
print 'false ' + str(correct['false'])
print 'rate ' + str(float(correct['true']) / float(correct['true'] + correct['false']))

fbase.close()
fsample.close()
ftag.close()
fw.close()
