#!/usr/bin/env python
# coding:utf8
# 整理较好的训练集，供后续实验使用

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
outputFile = '../data/trainset.txt'
fw = open(outputFile, 'w')

count = 10000
print "分析参考新闻"
for line in fbase:
	line = line.rstrip('\n').split('^')
	# 参考新闻标签
	news_id = count
	url = line[1]
	title = line[2]
	timestamp = line[3]
	tag = line[4]
	content = line[5]

	count += 1

	fw.write(str(news_id) + '^' + url + '^' + title + '^' + timestamp + '^' + tag + '^' + content + '\n')

sampleTag = {}
print "获取样本标签"
for line in ftag:
	line = line.rstrip('\n').split(',')
	news_id = line[0]
	error = line[1]
	tag = line[2]
	num = line[3]

	if float(error) == 0 and int(num) > 1:
		sampleTag[str(news_id)] = tag

print "分类样本新闻"
for line in fsample:
	line = line.rstrip('\n').split('^')
	news_id = line[0]
	title = line[1]
	url = line[2]
	timestamp = line[3]
	content = line[5]

	# 判断该新闻是否有学生标注
	if not sampleTag.has_key(str(news_id)):
		continue

	# 判断该新闻是否标题为空
	if title == '':
		continue

	fw.write(news_id + '^' + url + '^' + title + '^' + timestamp + '^' + sampleTag[news_id] + '^' + content + '\n')

fbase.close()
fsample.close()
ftag.close()
fw.close()
