#!/usr/bin/env python
# coding:utf8
# 在每个标签下生成时间线并汇总

import time
import math
import sys 
reload(sys)
sys.setdefaultencoding('utf8')
import jieba.analyse
import MySQLdb
import MySQLdb.cursors
import numpy as np
print 'load model'
import gensim
model = gensim.models.Word2Vec.load("../data/wiki.zh.text.model")
print 'load finish'

ISOTIMEFORMAT='%Y-%m-%d %X'

inputFile = '../data/trainset.txt'
fr = open(inputFile, 'r')

db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='timeline', port=8889, charset='utf8', cursorclass = MySQLdb.cursors.DictCursor)
db.autocommit(True)
cursor = db.cursor()
cursor.execute('delete from news where keyword=%s',['巴黎暴恐'])
cursor.execute('delete from timeline where keyword=%s',['巴黎暴恐'])

# 计算余弦距离
def cosine(s1, s2):
	inner = 0
	count = 0
	for k1, v1 in s1.items():
		for k2, v2 in s2.items():
			# if k1.find(k2) >= 0 or k2.find(k1) >= 0:
			# 	inner += v1 * v2
			try:
				inner += 10 * v1 * v2 * abs(model.similarity(k1.decode('utf8'), k2.decode('utf8')))
			except Exception, e:
				if k1 == k2:
					inner += 10 * v1 * v2
			else:
				pass
			finally:
				count += 1

	# return math.acos(float(inner) / float(norm1 * norm2 + 0.0000001))
	return float(inner) / (float(count) + 0.000000001)

def sentence2vector(sentence):
	# sentence = jieba.analyse.textrank(sentence, topK=999, withWeight=True, allowPOS=('nr','ns','nt','n','vn','v')) 
	sentence = jieba.analyse.extract_tags(sentence, topK=999, withWeight=True, allowPOS=())
	result = {}
	for item in sentence:
		result[item[0]] = item[1]
	return result

def get_most_important_sentences(title, content, N):
	title = sentence2vector(title)
	content = content.replace('\t', '。').replace('\n', '。')
	content = content.split('。')
	result = []
	for item in content:
		if len(item.decode('utf8')) < 30:
			continue
		item = item.strip()
		cos = cosine(title, sentence2vector(item))
		result.append((item, cos))
	result.sort(lambda x,y:cmp(x[1],y[1]),reverse=True)
	if len(result) > N:
		return result[:N]
	else:
		return result

print '计算特征向量'
print time.strftime( ISOTIMEFORMAT, time.localtime() )
count = 0
result = {}
titles = []
tmp = {}
times = []
for line in fr:
	count += 1
	print count

	line = line.rstrip('\n').split('^')
	news_id = line[0]
	url = line[1]
	title = line[2]
	timestamp = int(time.mktime(time.strptime(line[3], '%Y-%m-%d')))
	tag = line[4]
	content = line[5]

	if title in titles:
		continue
	titles.append(title)

	cursor.execute("insert into news(keyword,url,title,timestamp,tag,content,knowledge) values(%s,%s,%s,%s,%s,%s,'')",['巴黎暴恐',url,title,timestamp,tag,content])

	if not result.has_key(str(tag)):
		result[str(tag)] = []

	if not tmp.has_key(str(tag)):
		tmp[str(tag)] = []

	sentences = get_most_important_sentences(title, content, 5)

	# result[tag].append({'news_id': news_id, 'timestamp': timestamp, 'sentence': title, 'rank': 1})
	for item in sentences:
		if not item[0] in tmp[str(tag)]:
			tmp[str(tag)].append(item[0])
			times.append(timestamp)
			result[str(tag)].append({'news_id': news_id, 'timestamp': timestamp, 'sentence': item[0], 'title': title, 'rank': 1})	

print '特征向量计算结束'
print time.strftime( ISOTIMEFORMAT, time.localtime() )
print len(times)
tmean = np.median(times)
tstd = np.std(times)
print tmean,tstd
for key, value in result.items():
	print key, len(value)

def timeline(sentences, num):
	count = len(sentences)
	similarity = {}

	for x in xrange(0, count):
		sentences[x]['vector'] = sentence2vector(sentences[x]['sentence'])

	for x in xrange(0, count):
		similarity[str(x)] = {}
		for y in xrange(0, count):
			if x == y:
				similarity[str(x)][str(y)] = 0
			elif x > y:
				similarity[str(x)][str(y)] = similarity[str(y)][str(x)]
			else:
				similarity[str(x)][str(y)] = cosine(sentences[x]['vector'], sentences[y]['vector']) * math.exp(-abs(float(sentences[x]['timestamp'] - sentences[y]['timestamp']) / 3600 / 24 / 7))

	loop = 0
	ratio = []
	for x in xrange(0, count):
		ratio.append(math.exp(-(sentences[x]['timestamp'] - tmean) * (sentences[x]['timestamp'] - tmean) / (2 * tstd * tstd)))

	while True:
		loop += 1
		print '第' + str(loop) + '轮迭代'
		ranks = []
		total = np.sum([x['rank'] for x in sentences])
		for x in xrange(0, count):
			tmp = 0
			for y in xrange(0, count):
				tmp += float(sentences[y]['rank']) * similarity[str(y)][str(x)]
			ranks.append(tmp * ratio[x] / float(total))

		totalChange = 0
		for x in xrange(0, count):
			totalChange += abs(ranks[x] - sentences[x]['rank'])

		for x in xrange(0, count):
			sentences[x]['rank'] = ranks[x]

		print totalChange
		if totalChange  < 0.000000001 or loop == 1000:
			break

	sentences.sort(lambda x, y:cmp(x['rank'], y['rank']), reverse=True)

	if len(sentences) > num:
		sentences = sentences[:num]

	sentences.sort(lambda x, y:cmp(x['timestamp'], y['timestamp']), reverse=True)

	return sentences

for key, value in result.items():
	print 'tag ' + str(key)
	records = timeline(value, 9999)
	for item in records:
		print item['timestamp'], item['sentence'] + '(' + item['title'] + ')'
		cursor.execute('insert into timeline(keyword,timestamp,title,sentence,tag,rank) values(%s,%s,%s,%s,%s,%s)',['巴黎暴恐',item['timestamp'],item['title'],item['sentence'],key,item['rank']])

fr.close()
db.close()
cursor.close()