from collections import defaultdict
from pandas import read_table
import numpy as np
import math

class NaiveBayesClassfier:
    def __init__(self, k=0.5):
        self.k = k
        self.word_probs = []

    def load_corpus(self, path):
        # corpus : 말뭉치. 언어표본 집합. 형태소 분석
        corpus = read_table(path, sep=',', encoding='UTF-8')
        corpus = np.array(corpus)
        return corpus

    def count_words(self, training_set):
        # 학습데이터는 영화리뷰 본문(doc), 평점(point) 로 구성
        counts = defaultdict(lambda: [0,0]) # lambda 는 무명
        for doc, point in training_set:
            # 영화리뷰가 텍스트일때만 카운트
            if self.isNumber(doc) is False:
                # 리뷰를 띄어쓰기 단위로 토크나이징
                words = doc.split()
                for word in words:
                    counts[word][0 if point > 3.5 else 1] += 1
        return counts

    def isNumber(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def word_probabilities(self, counts, total_class0, total_class1, k):
        # 단어의 빈도수를 [단어, p(w|긍정), p(w|부정)] 형태로 변환
        return [(w,
                 (class0 + k) / (total_class0 + 2 * k),
                 (class1 + k) / (total_class1 + 2 * k)) # () 닫음
                for w, (class0, class1) in counts.items()]

    def class0_probability(self, word_probs, doc):
        # 별도의 토크나이즈 하지 않고 띄어쓰기만
        docwords = doc.split()
        # 초기값은 모두 0으로 처리
        log_prob_if_class0 = log_prob_if_class1 = 0.0
        # 모든 단어에 대한 반복
        for word, prob_if_class0, prob_if_class1 in word_probs:
            # 만약 리뷰에 word 가 나타나면 해당 단어가 나올 log 에 확률을 더해줌
            if word in docwords:
                log_prob_if_class0 += math.log(prob_if_class0)
                log_prob_if_class1 += math.log(prob_if_class1)
            # 만약 리뷰에 word 가 나타나지 않으면
            # 해당 단어가 나오지 않을 log 에 확률을 더해줌
            # 나오지 않을 확률은 log(1-나올확률)로 계산

            else:
                log_prob_if_class0 += math.log(1.0 - prob_if_class0)
                log_prob_if_class1 += math.log(1.0 - prob_if_class1)

        prob_if_class0 = math.exp(log_prob_if_class0)
        prob_if_class1 = math.exp(log_prob_if_class1)
        return prob_if_class0 / (prob_if_class0 + prob_if_class1)

    def train(self, path):
        training_set = self.load_corpus(path)
        # 범주0 (긍정) 과 범주1(부정) 문서의 수를 세어줌
        num_class0 = len([1 for _, point in training_set if point > 3.5])
        num_class1 = len(training_set) - num_class0
        word_counts = self.count_words(training_set)
        self.word_probs = self.word_probabilities(word_counts, num_class0, num_class1, self.k)

    def classfy(self, doc):
        return self.class0_probability(self.word_probs, doc)
















