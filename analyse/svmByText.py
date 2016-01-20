#!/usr/bin/env python
# coding:utf8
# 借助SVM和文本进行新闻分类

import jieba.posseg as pseg
from sklearn import svm
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
# 输出分类结果
# outputFile = '../data/news_ifeng_classified_dp.txt'
# fw = open(outputFile, 'w')

corpus = []

X_train = []
Y_train = []
X_test = []
Y_test = []
# 标题和正文权重比
alpha = 10

print "分析参考新闻"
for line in fbase:
	line = line.rstrip('\n').split('^')
	# 参考新闻标签
	title = line[2]
	tag = line[4]
	content = line[5]

	tmp = {}
	words = pseg.cut(title * alpha + content)
	for word, flag in words:
		if flag == 'x':
			continue
		if not tmp.has_key(word):
			tmp[word] = 0
		tmp[word] += 1
		if not word in corpus:
			corpus.append(word)
	X_train.append(tmp)
	Y_train.append(int(tag))

sampleTag = {}
print "获取样本标签"
for line in ftag:
	line = line.rstrip('\n').split(',')
	news_id = line[0]
	error = line[1]
	tag = line[2]
	num = line[3]

	if float(error) == 0 and int(num) > 1:
		sampleTag[str(news_id)] = int(tag)

print "分类样本新闻"
for line in fsample:
	line = line.rstrip('\n').split('^')
	news_id = line[0]
	title = line[1]
	url = line[2]
	date = line[3]
	content = line[5]

	# 判断该新闻是否有学生标注
	if not sampleTag.has_key(str(news_id)):
		continue

	# 判断该新闻是否标题为空
	if title == '':
		continue

	tmp = {}
	words = pseg.cut(title * alpha + content)
	for word, flag in words:
		if flag == 'x':
			continue
		if not tmp.has_key(word):
			tmp[word] = 0
		tmp[word] += 1
		if not word in corpus:
			corpus.append(word)
	X_test.append(tmp)
	Y_test.append(sampleTag[str(news_id)])

for x in xrange(0, len(X_train)):
	item = X_train[x]
	tmp = []
	for i in corpus:
		if not item.has_key(i):
			tmp.append(0)
		else:
			tmp.append(item[i])
	X_train[x] = tmp

for x in xrange(0, len(X_test)):
	item = X_test[x]
	tmp = []
	for i in corpus:
		if not item.has_key(i):
			tmp.append(0)
		else:
			tmp.append(item[i])
	X_test[x] = tmp

print len(X_train), len(X_train[0]), len(Y_train), len(X_test), len(Y_test)

print '使用SVM进行分类'
clf = svm.SVC()
clf.fit(X_train, Y_train)
prediction = clf.predict(X_test)

print prediction

result = {'true': 0, 'false': 0}
for x in xrange(0, len(prediction)):
	if prediction[x] == Y_test[x]:
		result['true'] += 1
	else:
		result['false'] += 1
print result['true'], result['false']

fbase.close()
fsample.close()
ftag.close()
# fw.close()
