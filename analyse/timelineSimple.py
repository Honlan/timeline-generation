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
			try:
				inner += v1 * v2 * abs(model.similarity(k1.decode('utf8'), k2.decode('utf8')))
			except Exception, e:
				pass
			else:
				pass
			finally:
				pass

	return inner

def sentence2vector(sentence):
	sentence = jieba.analyse.textrank(sentence, topK=50, withWeight=True, allowPOS=('nr','ns','nt','n','vn','v')) 
	# sentence = jieba.analyse.extract_tags(sentence, topK=10, withWeight=True, allowPOS=())
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
result = []
titles = []
tmp = {}
corpus = ''
for line in fr:
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

	if not tmp.has_key(str(tag)):
		tmp[str(tag)] = []

	sentences = get_most_important_sentences(title, content, 5)
	sentences = [x[0] for x in sentences]

	for item in sentences:
		if item == '':
			continue

		if item in tmp[str(tag)]:
			continue

		tmp[str(tag)].append(item)
		corpus += item
		result.append({'news_id': news_id, 'tag': tag, 'timestamp': timestamp, 'sentence': item, 'title': title, 'rank': 1, 'vector': sentence2vector(item)})	

print '特征向量计算结束'
print time.strftime( ISOTIMEFORMAT, time.localtime() )
print len(result)

corpus = sentence2vector(corpus)

aveTime = []
for item in result:
	aveTime.append(item['timestamp'])
aveTime.sort(lambda x,y:cmp(x,y))
aveTime = aveTime[int(len(aveTime)/2)]

for item in result:
	item['rank'] = cosine(item['vector'], corpus) * math.exp(-0.02 * abs(float(item['timestamp'] - aveTime) / 3600 / 24))

result.sort(lambda x,y:cmp(x['rank'],y['rank']),reverse=True)

for x in ['1','2','3','4','6','7']:
	num = 0
	for item in result:
		if item['tag'] == x:
			cursor.execute('insert into timeline(keyword,timestamp,title,sentence,tag,rank) values(%s,%s,%s,%s,%s,%s)',['巴黎暴恐',item['timestamp'],item['title'],item['sentence'],item['tag'],item['rank']])
			num += 1
			if num == 20:
				break

print '得分排序计算结束'
print time.strftime( ISOTIMEFORMAT, time.localtime() )

fr.close()
db.close()
cursor.close()