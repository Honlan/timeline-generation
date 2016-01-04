#!/usr/bin/env python
# coding:utf8

import redis
import time
import threading
import urllib2
import random
from bs4 import BeautifulSoup
# from newspaper import Article

ISOTIMEFORMAT='%Y-%m-%d %X'

outputFile = '../data/test.txt'
r = redis.StrictRedis(host='localhost', password='root', port=6379, db=0)
r.setnx('search_id', 0)
search_id = r.incr('search_id')
r.set('page_id_%d' % search_id, -1)

keyword = '巴黎暴恐'
headers = {}
headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"

# 子线程数量
urlThread = 10
crawlThread = 20

# 获取url子线程
def access():
	global urlThread

	while 1:
		page_id = r.incr('page_id_%d' % search_id)

		# 检查是否还有新的索引任务
		if page_id < 0:
			urlThread -= 1
			if urlThread == 0:
				r.delete('page_id_%d' % search_id)
				print '已获取所有索引'
				print time.strftime( ISOTIMEFORMAT, time.localtime() )
			return

		if page_id > 20:
			r.set('page_id_%d' % search_id, -999)
			continue

		url = 'http://zhannei.baidu.com/cse/search?q=' + keyword + '&p=' + str(page_id) + '&s=16378496155419916178&entry=1&area=2'

		request = urllib2.Request(url=url, headers=headers)
		response = urllib2.urlopen(request)
		html = response.read()
		html = BeautifulSoup(html)
		result = html.select('.c-title a')

		for item in result:
			href = item.get('href')
			if href.split('//')[1][:4] == 'news' and href[-4:] == 'html' and not r.sismember('urls_%d' % search_id, href):
				r.sadd('urls_%d' % search_id, href)

# 获取新闻内容子线程
def crawl():
	global urlThread
	global crawlThread

	while 1:
		if urlThread == 0 and r.scard('urls_%d' % search_id) == 0:
			crawlThread -= 1
			if crawlThread == 0:
				print '已获取所有新闻内容'
				print time.strftime( ISOTIMEFORMAT, time.localtime() )
				fw.close()
				r.delete('urls_%d' % search_id)
			return 

		target = r.spop('urls_%d' % search_id)
		# 判断是否有url剩余
		if target == None:
			time.sleep(random.random())
			continue

		try:
			request = urllib2.Request(url=target, headers=headers)
			response = urllib2.urlopen(request)
			html = response.read()
			html = BeautifulSoup(html)
			title = html.select('#artical_topic')[0].get_text().split('(')[0].strip()
			timestamp = html.select('.ss01')[0].get_text().strip()
			content = html.select('#main_content p')
			tmp = ''
			for item in content:
				if item.get_text() == '':
					continue
				tmp += item.get_text() + '\t'
			content = tmp
			# images = html.select('#main_content img')
		except Exception, e:
			pass
		else:
			fw.write(target + '^' + title.encode('utf8') + '^' + timestamp.encode('utf8') + '^' + content.encode('utf8') + '\n')
		finally:
			pass

if __name__ == "__main__":
	print 'search_id: ' + str(search_id) + ' ' + keyword
	print time.strftime( ISOTIMEFORMAT, time.localtime() )

	fw = open(outputFile, 'w')

	for x in xrange(0, urlThread):
		threading.Thread(target=access, name='Accessor_%d' % x).start()

	time.sleep(0.5)

	for x in xrange(0, crawlThread):
		threading.Thread(target=crawl, name='Crawler_%d' % x).start()
