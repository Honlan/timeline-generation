#!/usr/bin/env python
# coding:utf-8
# 去除重复新闻

import time

inputFile = "../data/news.txt"
outputFile = "../data/news_unique.txt"
fr = open(inputFile, 'r')
fw = open(outputFile, 'w')

ISOTIMEFORMAT='%Y-%m-%d %X'

result = {}
count = 0
total = 0

print '去重开始'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

for line in fr:
	total = total + 1
	temp = line.split('^')

	if not (temp[4][0:4] == '2015'):
		continue

	if result.has_key(temp[1]):
		continue
	else:
		result[temp[1]] = 1
		count = count + 1
		fw.write(line)

print '去重结束'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

print '原始数据共' + str(total) + '条，去重后共' + str(count) + '条' 

fr.close()
fw.close()