#!/usr/bin/env python
# coding:utf8
# 借助grocery包进行新闻分类

from tgrocery import Grocery
import sys 
reload(sys)
sys.setdefaultencoding('utf8')

grocery = Grocery('paris')

inputFile = '../data/news_standard.txt'
# 参考新闻的url和分类
fbase = open(inputFile, 'r')
inputFile = '../data/news_ifeng.txt'
# 待分类的数据
fsample = open(inputFile, 'r')
outputFile = '../data/news_ifeng_classified_grocery.txt'
fw = open(outputFile, 'w')

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
		tag = '各方态度'
	elif int(tag) == 4:
		tag = '事件演化'
	elif int(tag) == 6:
		tag = '直接关联'
	elif int(tag) == 7:
		tag = '暂无关联'

	# 记录term vector
	bases.append((tag, title))

grocery.train(bases)
grocery.save()
new_grocery = Grocery('paris')
new_grocery.load()

tagStat = {}
print "分类样本新闻"
for line in fsample:
	line = line.rstrip('\n').split('^')
	title = line[1]
	url = line[2]
	tag = new_grocery.predict(title)
	print tag + '\t' + title

	# 统计各个标签出现次数
	if not tagStat.has_key(tag):
		tagStat[tag] = 1
	else:
		tagStat[tag] += 1

	fw.write(tag + '^' + title + '^' + url + '\n')

for key, value in tagStat.items():
	print key, value

fbase.close()
fsample.close()
fw.close()
