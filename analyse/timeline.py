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
print 'load model'
import gensim
model = gensim.models.Word2Vec.load("../data/wiki.zh.text.model")
print 'load finish'

ISOTIMEFORMAT='%Y-%m-%d %X'

inputFile = '../data/trainset.txt'
fr = open(inputFile, 'r')
outputFile = '../data/timeline.txt'
fw = open(outputFile, 'w')

db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='timeline', port=8889, charset='utf8', cursorclass = MySQLdb.cursors.DictCursor)
db.autocommit(True)
cursor = db.cursor()
cursor.execute('delete from news where keyword=%s',['巴黎暴恐'])
cursor.execute('delete from timeline where keyword=%s',['巴黎暴恐'])

# 计算余弦距离
def cosine(s1, s2):
	inner = 0
	for k1, v1 in s1.items():
		for k2, v2 in s2.items():
			# if k1.find(k2) >= 0 or k2.find(k1) >= 0:
			# 	inner += v1 * v2
			try:
				inner += v1 * v2 * abs(model.similarity(k1.decode('utf8'), k2.decode('utf8')))
			except Exception, e:
				pass
			else:
				pass
			finally:
				pass
	norm1 = 0
	tmp = s1
	for k1, v1 in s1.items():
		for k, v in tmp.items():
			try:
				norm1 += v1 * v * abs(model.similarity(k1.decode('utf8'), k.decode('utf8')))
			except Exception, e:
				pass
			else:
				pass
			finally:
				pass
	norm1 = math.sqrt(norm1)

	norm2 = 0
	tmp = s2
	for k2, v2 in s2.items():
		for k, v in tmp.items():
			try:
				norm2 += v2 * v * abs(model.similarity(k2.decode('utf8'), k.decode('utf8')))
			except Exception, e:
				pass
			else:
				pass
			finally:
				pass
	norm2 = math.sqrt(norm1)

	# return math.acos(float(inner) / float(norm1 * norm2 + 0.0000001))
	return float(inner) / float(norm1 * norm2 + 0.0000001)

def sentence2vector(sentence):
	# sentence = jieba.analyse.textrank(sentence, topK=999, withWeight=True, allowPOS=('nr','ns','nt','n','vn','v')) 
	sentence = jieba.analyse.extract_tags(sentence, topK=999, withWeight=True, allowPOS=())
	result = {}
	for item in sentence:
		result[item[0]] = item[1]
	return result

def get_most_important_sentences(title, content, N):
	title = sentence2vector(title)
	content = content.split('。')
	result = []
	for item in content:
		if item == '':
			continue
		item = item.replace('\t', '').replace('\n', '').strip()
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

	cursor.execute("insert into news(keyword,url,title,timestamp,tag,content) values(%s,%s,%s,%s,%s,%s)",['巴黎暴恐',url,title,timestamp,tag,content])

	if not result.has_key(str(tag)):
		result[str(tag)] = []

	if not tmp.has_key(str(tag)):
		tmp[str(tag)] = []

	sentences = get_most_important_sentences(title, content, 5)

	# result[tag].append({'news_id': news_id, 'timestamp': timestamp, 'sentence': title, 'rank': 1})
	for item in sentences:
		if not item[0] in tmp[str(tag)]:
			tmp[str(tag)].append(item[0])
			result[str(tag)].append({'news_id': news_id, 'timestamp': timestamp, 'sentence': item[0], 'title': title, 'rank': 1})	

print '特征向量计算结束'
print time.strftime( ISOTIMEFORMAT, time.localtime() )
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
				continue
			elif x > y:
				similarity[str(x)][str(y)] = similarity[str(y)][str(x)]
			else:
				similarity[str(x)][str(y)] = cosine(sentences[x]['vector'], sentences[y]['vector']) * math.exp(-0.02 * abs(float(sentences[x]['timestamp'] - sentences[y]['timestamp']) / 3600 / 24))

		total = 0
		for y in xrange(0, count):
			if y == x:
				continue
			total += similarity[str(x)][str(y)]
		similarity[str(x)]['total'] = total

	loop = 0
	while True:
		loop += 1
		print '第' + str(loop) + '轮迭代' 
		ranks = []
		for x in xrange(0, count):
			tmp = 0
			for y in xrange(0, count):
				if y == x:
					continue
				else:
					tmp += sentences[y]['rank'] * similarity[str(y)][str(x)] / (similarity[str(y)]['total'] + 0.0000001)
			ranks.append(tmp)

		totalChange = 0
		for x in xrange(0, count):
			totalChange += abs(ranks[x] - sentences[x]['rank'])

		for x in xrange(0, count):
			sentences[x]['rank'] = ranks[x]

		print totalChange
		if totalChange < 0.0001 or loop == 1000:
			break

	sentences.sort(lambda x, y:cmp(x['rank'], y['rank']), reverse=True)

	if len(sentences) > num:
		sentences = sentences[:num]

	sentences.sort(lambda x, y:cmp(x['timestamp'], y['timestamp']), reverse=True)

	for item in sentences:
		item['timestamp'] = time.strftime('%Y-%m-%d', time.localtime(item['timestamp']))

	return sentences

for key, value in result.items():
	print 'tag ' + str(key)
	fw.write(key + '\n')
	records = timeline(value, 20)
	for item in records:
		print item['timestamp'], item['sentence'] + '(' + item['title'] + ')'
		cursor.execute('insert into timeline(keyword,timestamp,title,sentence,tag) values(%s,%s,%s,%s,%s)',['巴黎暴恐',item['timestamp'],item['title'],item['sentence'],key])
		fw.write(item['timestamp'] + '^' + item['news_id'] + '^' + item['sentence'] + '\n')
	fw.write('\n')

fr.close()
fw.close()
db.close()
cursor.close()