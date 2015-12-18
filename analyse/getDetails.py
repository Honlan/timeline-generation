#!/usr/bin/env python
# coding:utf-8
# 根据新闻url，借助newspaper包获取详细内容

import time 
from newspaper import Article

fr = open("../data/news_unique.txt", 'r')
fw = open("../data/news_details.txt", 'w')

count = 0

for line in fr:
	count += 1
	print count

	line = line.split('^')
	Id = line[0]
	title = line[1]
	url = line[2]
	source = line[3]
	timestamp = line[4]
	abstract = line[5]
	print abstract

	try:
		article = Article(url, language='zh')
		article.download()
		article.parse()
		content = article.text
		content = content.replace('\n', '\\')
	except Exception, e:
		content = ''
	else:
		pass
	finally:
		pass

	fw.write(Id + '^' + title + '^' + url + '^' + source + '^' + timestamp + '^' + abstract + '^' + content.encode('utf8') + '\n')

fr.close()
fw.close()

