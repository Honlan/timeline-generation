#!/usr/bin/env python
# coding:utf8
# 借助深度学习和文本进行新闻分类

import jieba.analyse
import numpy as np
np.random.seed(1337)  # for reproducibility
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.utils import np_utils
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
	words = jieba.analyse.textrank(title * alpha + content, topK=30, withWeight=True, allowPOS=('nr','ns','nt','n','vn','v')) 
	for item in words:
		tmp[item[0]] = item[1]
		if not item[0] in corpus:
			corpus.append(item[0])
	X_train.append(tmp)
	Y_train.append(int(tag))

sampleTag = {}
print "获取学生对样本新闻所打标签"
for line in ftag:
	line = line.rstrip('\n').split(',')
	news_id = line[0]
	error = line[1]
	tag = line[2]
	num = line[3]

	if float(error) == 0 and int(num) > 1:
		sampleTag[str(news_id)] = int(tag)

# 一次性增强训练集
'''
print "一次性增强训练集"
for line in fsample:
	line = line.rstrip('\n').split('^')
	news_id = line[0]
	title = line[1]
	if sampleTag.has_key(str(news_id)) and float(sampleTag[str(news_id)]['error']) == 0:
		bases.append((sampleTag[str(news_id)]['tag'], title))
print len(bases)
fsample.close()
inputFile = '../data/news_ifeng.txt'
fsample = open(inputFile, 'r')
'''

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
	words = jieba.analyse.textrank(title * alpha + content, topK=30, withWeight=True, allowPOS=('nr','ns','nt','n','vn','v')) 
	for item in words:
		tmp[item[0]] = item[1]
		if not item[0] in corpus:
			corpus.append(item[0])
	X_test.append(tmp)
	Y_test.append(sampleTag[str(news_id)])

	# 渐进式增强训练集
	'''
	# 将方差为零的样本加入基准集
	if float(sampleTag[str(news_id)]['error']) == 0:
	# if True:
		bases.append((sampleTag[str(news_id)]['tag'], title))
		print "添加一条基准数据"
		grocery.train(bases)
		grocery.save()
		new_grocery = Grocery('paris')
		new_grocery.load()
	'''

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

print '使用深度学习进行分类'
batch_size = 4
nb_epoch = 5
X_train = np.array(X_train)
X_test = np.array(X_test)
nb_classes = np.max(Y_test) + 1
Y_train = np_utils.to_categorical(Y_train, nb_classes)
Y_test = np_utils.to_categorical(Y_test, nb_classes)
print X_train.shape, Y_train.shape, X_test.shape, Y_test.shape

model = Sequential()
model.add(Dense(512, input_dim=X_train.shape[1], activation='softmax'))
# model.add(Dropout(0.1))
model.add(Dense(128, activation='softmax'))
model.add(Dense(32, activation='softmax'))
model.add(Dense(nb_classes, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam')

history = model.fit(X_train, Y_train, nb_epoch=nb_epoch, batch_size=batch_size, verbose=1, show_accuracy=True, validation_split=0.1)
score = model.evaluate(X_test, Y_test, batch_size=batch_size, verbose=1, show_accuracy=True)
print('Test score:', score[0])
print('Test accuracy:', score[1])

fbase.close()
fsample.close()
ftag.close()
# fw.close()
