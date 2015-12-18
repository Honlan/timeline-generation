#!/usr/bin/env python
# coding:utf8

import urllib2
import urllib
import time
from newspaper import Article
from bs4 import BeautifulSoup

outputFile = '../data/ifeng.txt'
fw = open(outputFile, 'w')
fw.write('id^title^url^timestamp^cover^content\n')

headers = {}
# headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
# headers["Accept-Encoding"] = "gzip, deflate, sdch"
# headers["Accept-Language"] = "zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2"
# headers["Cache-Control"] = "max-age=0"
# headers["Connection"] = "keep-alive"
# headers["Cookie"] = 'asdasd13323efafasfa'
# headers["Host"] = "movie.douban.com"
# headers["Referer"] = "http://movie.douban.com/"
# headers["Upgrade-Insecure-Requests"] = 1
headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"

count = 0
pageNum = 0
searchUrl = 'http://zhannei.baidu.com/cse/search?q=巴黎+恐怖袭击&p=' + str(pageNum) + '&s=16378496155419916178&entry=1&area=2'

while pageNum < 75:
	request = urllib2.Request(url=searchUrl, headers=headers)
	response = urllib2.urlopen(request)
	html = response.read()
	html = BeautifulSoup(html)

	urls = html.select('.c-title a')

	timestamps = html.select('.c-showurl')

	idx = 0

	for item in urls:
		url = item.get('href')

		while True:
			try:
				article = Article(url, language='zh')
				article.download()
				article.parse()
				content = article.text
				content = content.replace('\n', '\t')
				title = article.title
				cover = article.top_image
				timestamp = timestamps[idx].get_text().split('... ')[1]
			except Exception, e:
				pass
			else:
				idx += 1
				count += 1
				print count
				fw.write(str(count) + '^' + title.encode('utf8') + '^' + url.encode('utf8') + '^' + timestamp.encode('utf8') + '^' + cover.encode('utf8') + '^' + content.encode('utf8') + '\n')
				time.sleep(5)
				break
			finally:
				pass
	
	pageNum += 1
	searchUrl = 'http://zhannei.baidu.com/cse/search?q=巴黎+恐怖袭击&p=' + str(pageNum) + '&s=16378496155419916178&entry=1&area=2'

print pageNum, count

# for line in fr:
# 	if firstLine:
# 		firstLine = False
# 		continue

# 	line = line.split(';')

# 	movieId = line[0]
# 	title = line[1]
# 	url = line[2]
# 	cover = line[3]
# 	rate = line[4].rstrip('\n')

# 	if result.has_key(movieId):
# 		continue
# 	else:
# 		result[str(movieId)] = 1

# 	try:
# 		request = urllib2.Request(url=url,headers=headers)
# 		# request = urllib2.Request(url=url)
# 		response = urllib2.urlopen(request)
# 		html = response.read()
# 		html = BeautifulSoup(html)

# 		info = html.select('#info')[0]
# 		info = info.get_text().split('\n')

# 		director = info[1].split(':')[-1].strip()
# 		composer = info[2].split(':')[-1].strip()
# 		actor = info[3].split(':')[-1].strip()
# 		category = info[4].split(':')[-1].strip()
# 		district = info[6].split(':')[-1].strip()
# 		language = info[7].split(':')[-1].strip()
# 		showtime = info[8].split(':')[-1].strip()
# 		length = info[9].split(':')[-1].strip()
# 		othername = info[10].split(':')[-1].strip()

# 		description = html.find_all("span", attrs={"property": "v:summary"})[0].get_text()
# 		description = description.lstrip().lstrip('\n\t').rstrip().rstrip('\n\t').replace('\n','\t')

# 		record = str(movieId) + '^' + title + '^' + url + '^' + cover + '^' + str(rate) + '^' + director.encode('utf8') + '^' + composer.encode('utf8') + '^' + actor.encode('utf8') + '^' + category.encode('utf8') + '^' + district.encode('utf8') + '^' + language.encode('utf8') + '^' + showtime.encode('utf8') + '^' + length.encode('utf8') + '^' + othername.encode('utf8') + '^' + description.encode('utf8') + '\n'
# 		fw.write(record)
# 		print count,title
# 		time.sleep(5)
	
# 	except Exception, e:
# 		print e
# 		print count,title,"Error"
# 		errorCount = errorCount + 1
# 	else:
# 		pass
# 	finally:
# 		pass

# 	count = count + 1
	
# print count, errorCount

fw.close()