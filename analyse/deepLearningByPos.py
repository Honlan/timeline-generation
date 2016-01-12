#!/usr/bin/env python
# coding:utf8
# 借助深度学习和词性进行新闻分类

import jieba.posseg as pseg
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

allPos = ['ns','n','q','v','m','s','t','r','nr','d','vn','p','nt','a','nz','j','l','f','c','uj','an','nrt','nrfg','ng','i','y','vg','u','mq','ad','ul','ud','z','b','df','k','ug','eng','uv','zg','ag','vd','uz','o','tg','rr','h','rz','vq','g']

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
		if not tmp.has_key(flag):
			tmp[flag] = 0
		tmp[flag] += 1
	vec = []
	for item in allPos:
		if not tmp.has_key(item):
			vec.append(0)
		else:
			vec.append(tmp[item])
	X_train.append(vec)
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
	words = pseg.cut(title * alpha + content)
	for word, flag in words:
		if not tmp.has_key(flag):
			tmp[flag] = 0
		tmp[flag] += 1
	vec = []
	for item in allPos:
		if not tmp.has_key(item):
			vec.append(0)
		else:
			vec.append(tmp[item])
	X_test.append(vec)
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

print '使用深度学习进行分类'
batch_size = 4
nb_epoch = 5
nb_classes = np.max(Y_test) + 1
X_train = np.array(X_train)
X_test = np.array(X_test)
Y_train = np_utils.to_categorical(Y_train, nb_classes)
Y_test = np_utils.to_categorical(Y_test, nb_classes)

model = Sequential()
model.add(Dense(512, input_dim=X_train.shape[1]))
model.add(Activation('relu'))
model.add(Dropout(0.1))
model.add(Dense(nb_classes))
model.add(Activation('softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam')

history = model.fit(X_train, Y_train, nb_epoch=nb_epoch, batch_size=batch_size, verbose=1, show_accuracy=True, validation_split=0.1)
score = model.evaluate(X_test, Y_test, batch_size=batch_size, verbose=1, show_accuracy=True)
print('Test score:', score[0])
print('Test accuracy:', score[1])

fbase.close()
fsample.close()
ftag.close()
# fw.close()
