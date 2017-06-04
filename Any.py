#encoding:utf-8
import jieba
from gensim import corpora
from collections import defaultdict

class Analysis:

	def preteat_clause(self,phase):
		#分句
		cut_list = list('。！~？!?…')
		reslist,i,start = [],0,0
		for word in phase:
			if word in cut_list:
				reslist.append(phase[start:i])
				start = i+1
				i += 1
			else:
				i += 1

		if start < len(phase):
			reslist.append(phase[start:])

		return reslist

	def cutwords_jieba(self,sentence,userdict='dict/userdict.txt',stopwords='dict/stopwords.txt'):
		stropw = []
		if userdict:
			jieba.load_userdict(userdict)
			stropw = [line.strip() for line in open(stopwords,'r',encoding='utf-8').readlines()]

		frequency = defaultdict(int)
		l = list(jieba.cut(sentence))
		for t in l:
			frequency[t] += 1

		texts = [token for token in frequency if frequency[token] > 0]

		rtexts = list(set(texts)-set(stropw))
		return rtexts

	def deal_wrap(self,filedict):
		temp = []
		for x in open(filedict,'r',encoding='utf-8').readlines():
			temp.append(x.strip())
		return temp

	def sentiment_init(self):
		# 情感词典
		self.posdict = self.deal_wrap('dict/emotion_dict/pos_all_dict.txt')
		self.negdict = self.deal_wrap('dict/emotion_dict/neg_all_dict.txt')
		# 程度副词词典
		self.mostdict = self.deal_wrap('dict/degree_dict/most.txt')   # 权值为2
		self.verydict = self.deal_wrap('dict/degree_dict/very.txt')   # 权值为1.5
		self.moredict = self.deal_wrap('dict/degree_dict/more.txt')  # 权值为1.25
		self.ishdict = self.deal_wrap('dict/degree_dict/ish.txt')   # 权值为0.5
		self.insufficientdict = self.deal_wrap('dict/degree_dict/insufficiently.txt')  # 权值为0.25
		self.inversedict = self.deal_wrap('dict/degree_dict/inverse.txt')  # 权值为-1

	def cal_score(self,word, sentence_score):
		if word in self.mostdict:
			sentence_score *= 2.0
		elif word in self.verydict:
			sentence_score *= 1.75
		elif word in self.moredict:
			sentence_score *= 1.5
		elif word in self.ishdict:
			sentence_score *= 1.2
		elif word in self.insufficientdict:
			sentence_score *= 0.5
		elif word in self.inversedict:
			sentence_score *= -1
		return sentence_score

	def sentiment(self,sentence):
		i,s,posscore,negscore = 0,0,0,0
		for word in sentence:
			if word in self.posdict:
				posscore += 1 
				for w in sentence[s:i]:
					posscore = self.cal_score(w, posscore)
				s = i + 1 

			elif word in self.negdict: 
				negscore += 1
				for w in sentence[s:i]:
					negscore = self.cal_score(w, negscore)
				s = i + 1
			i+=1

		return posscore,negscore
		
a = Analysis()
a.sentiment_init()

total_pscore,total_nscore = 0,0

for tempstr in a.deal_wrap('data/data1.txt'):
	sentence_pscore,sentence_nscore = 0,0
	for x in a.preteat_clause(tempstr):
		c = a.cutwords_jieba(x,'','')
		posscore,negscore = a.sentiment(c)
		sentence_pscore += posscore
		sentence_nscore += negscore

	total_pscore += sentence_pscore
	total_nscore += sentence_nscore
	print(posscore,negscore,posscore-negscore)
	# print('单句：{}得分：\nposscore:{};negscore:{};totalscore:{}\n\n'.format(tempstr,sentence_pscore,sentence_nscore,sentence_pscore-sentence_nscore))


print('最后总得分：posscore:{};negscore:{};totalscore:{}'.format(total_pscore,total_nscore,total_pscore-total_nscore))