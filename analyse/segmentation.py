#!/usr/bin/env python
# coding:utf-8
# 使用结巴分词提取关键词

import jieba
import jieba.analyse
import time

inputFile = '../data/news_unique.txt'
fr = open(inputFile, 'r')
outputFile = '../data/keywords.txt'
fw = open(outputFile, 'w')

ISOTIMEFORMAT='%Y-%m-%d %X'

# 允许并行
jieba.enable_parallel(10)

def extract(content):
	return jieba.analyse.textrank(content, topK=100, withWeight=True, allowPOS=('nr','ns','nt','n','vn','v')) 
	# return jieba.analyse.extract_tags(content, topK=100, withWeight=True, allowPOS=('nr','ns','nt','n','vn','v'))

print '关键词提取开始'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

title = {}
abstract = {}

for line in fr:
	line = line.rstrip('\n').split('^')
	timestamp = line[4]
	timestamp = timestamp[0:timestamp.find(' ')]
	timestamp = timestamp[7:]
	timestamp = timestamp.replace('月', '-')
	timestamp = timestamp.replace('日', '')

	if not title.has_key(timestamp):
		title[timestamp] = ''
	title[timestamp] += line[1] + ' '

	if not abstract.has_key(timestamp):
		abstract[timestamp] = ''
	abstract[timestamp] += line[5] + ' '

result = ''

# 提取标题关键词
overall = ''
for key, value in title.items():
	overall += value + ' '
	words = extract(value)
	result += '"' + key + '":{'
	tmp = ''
	for k, v in words:
		tmp += k + ' ' + str('%.3f'%v) + ','
		result += '"' + k + '":' + str('%.3f'%v) + ','
	result += '},'
	fw.write('title;' + key + ';' + (tmp[:-1]).encode('utf8') + '\n')
words = extract(overall)
tmp = ''
result += '"all":{'
for k, v in words:
	tmp += k + ' ' + str('%.3f'%v) + ','
	result += '"' + k + '":' + str('%.3f'%v) + ','
fw.write('title;all;' + (tmp[:-1]).encode('utf8') + '\n')
result = result[:-1] + '}'

print result

result = ''

# 提取摘要关键词
overall = ''
for key, value in abstract.items():
	overall += value + ' '
	words = extract(value)
	result += '"' + key + '":{'
	tmp = ''
	for k, v in words:
		tmp += k + ' ' + str('%.3f'%v) + ','
		result += '"' + k + '":' + str('%.3f'%v) + ','
	result += '},'
	fw.write('abstract;' + key + ';' + (tmp[:-1]).encode('utf8') + '\n')
words = extract(overall)
tmp = ''
result += '"all":{'
for k, v in words:
	tmp += k + ' ' + str('%.3f'%v) + ','
	result += '"' + k + '":' + str('%.3f'%v) + ','
fw.write('abstract;all;' + (tmp[:-1]).encode('utf8') + '\n')
result = result[:-1] + '}'

print result

print '关键词提取结束'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

fr.close()
fw.close()