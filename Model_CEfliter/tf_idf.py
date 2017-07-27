# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import sys
sys.path.append("..")
from cmySecCEIntensity import cmySecCE
from sxpPackage import *
from cmyToolkit import *

#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class TfIdf:
    def __init__(self, pickle_path):
        self.section2sentence_id_list = {}
        self.text = LoadSxptext(pickle_path)
        self.words = self.text.sentence_tfidf.word
        self.count_words = []
        self.idx_s = []
        self.ranked_sentences = []
        self.get_sentence_weight()
        self.rank_sentences()
        self.ordered_sentence_id_set()

    def get_sentence_weight(self):
        # -- get stopwords list --
        f = open(os.path.join(corpdir, 'stopwords.txt'), 'r')
        lines = f.readlines()
        f.close()
        stopwords = [line.strip() for line in lines]
        # -- visit each sentence and get words and their appearance times in main body --
        sentences = self.text.sentenceset
        words_count = {}
        for sent in sentences:
            # get words in current sentence that are not stopwords and contains only a~zA~Z
            words = sent.sentence_text.split()
            words = [word.lower() for word in words]
            words = [word for word in words if word not in stopwords
                     and re.match(r'^[a-zA-Z]+$', word) is not None]
            # count word and update key and value in words_count
            for word in words:
                if word in words_count:
                    words_count[word] += 1
                else:
                    words_count[word] = 1
        # -- get (appearance times, words) list, and sort them by their appearance times reversely
        aux = [(words_count[k], k) for k in words_count.keys()]
        aux.sort(reverse=True)
        self.count_words = aux

    def rank_sentences(self):
        # -- get stopwords list --
        f = open(os.path.join(corpdir, 'stopwords.txt'), 'r')
        lines = f.readlines()
        f.close()
        stopwords = [line.strip() for line in lines]
        # get the non-stopwords indexes in token list
        idx = [i for i in range(len(self.words)) if self.words[i] not in stopwords
                      and re.match(r'^[a-zA-Z]+$', self.words[i]) is not None]
        # get the words_sentences matrix, which are all tf_idf values on sentence_level
        w_s = matrix(self.text.s_k.toarray()).T
        # -- strip stopwords and get non-stopwords tfidf value for each sentence--
        sentences2words = []
        for i in idx:
            sentences2words.append(array(w_s[i, :]).tolist())
        # -- sumup all non-stop words' tf-idf value as the sentences' weight
        e = matrix(ones(len(sentences2words))).T
        sentence_weight = matrix(array(sentences2words)).T * e
        # -- rank the sentence by their weight reversely and return a list of their original index --
        self.idx_s = argsort(array(-sentence_weight), axis=0)

    def ordered_sentence_id_set(self):
        self.ranked_sentences = [self.text.sentenceset[self.idx_s[i, 0]]
                            for i in range(len(self.text.sentenceset))]
        sec_titles = []
        for sec in self.text.section_list:
            self.section2sentence_id_list[sec.title] = []
            sec_titles.append(sec.title)
        for sentence in self.ranked_sentences:
            section_tag = self.text.paraset[sentence.id_para].section_title
            if section_tag != '' and section_tag in sec_titles:
                self.section2sentence_id_list[section_tag].append(sentence.id)

    def OutputAllRankSentence(self, useabstr=1, maxwords=-1):
        sent_txt_set = []
        for sentence in self.ranked_sentences:
            sent_txt_set.append(sentence.sentence_text)
        return sent_txt_set

    # ---- return top k sentence_text ----
    def OutPutTopKSent(self, topk, useabstr = 1, maxwords = -1):
        i = 0  # i stores how many sentences have been append into sent_txt_set
        wordlen = 0  # wordlen stores how many str has been append into sent_txt_set
        # useabstr == 1, use number of str in abstract as the maxwords
        if useabstr == 1:
            abstractlen = len(self.text.abstract)
        # useabstr == 2, use number of str in conclusion as the maxwords
        elif useabstr == 2:
            abstractlen = len(self.text.conclusion)
        # useabstr == 3, use number of str in abstract and conclusion as the maxwords
        elif useabstr == 3:
            abstractlen = len(self.text.abstract) + len(self.text.conclusion)
        else:
            abstractlen = 0
        # -- get top k sentence --
        sent_txt_set = []
        for sentence in self.ranked_sentences:
            # ignore sentence that contains less than 2 str
            if len(sentence.sentence_text) <= 1:
                continue
            # useabstr in [1,2,3] means use abstractlen as str upper found
            if wordlen >= abstractlen and useabstr in [1, 2, 3]:
                break
            # useabstr == 0 means use maxwords as str upper bound
            if wordlen >= maxwords and useabstr == 0:
                break
            # useabstr == -1 means use topk as sentences upper bound
            if i >= topk and useabstr == -1:
                break
            sent_txt_set.append(sentence.sentence_text)
            wordlen += len(sentence.sentence_text)
            i += 1
        return sent_txt_set

#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def test_tfidf():
    pk = r'E:\Programs\Eclipse\CE_relation\CEsummary\kg\pickle_SecCE\f0001.txt_abstract.pk'
    tfidf = TfIdf(pk)
    # for k, v in tfidf.count_words:
    #     print v, k
    topksent = 10
    tops = tfidf.OutPutTopKSent(topksent, 0, 500)
    for i, eachs in enumerate(tops):
        print '----------------'
        print i, eachs

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
def main():
    test_tfidf()

if __name__ == '__main__':
    main()



