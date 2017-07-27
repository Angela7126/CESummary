# -------------------------------------------------------------------------------
# Name:        sxpContextModel
# Purpose:
#
# Author:      sunxp
#
# Created:     26/10/2015
# Copyright:   (c) sunxp 2015
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# -*- coding: UTF-8 -*-

### Notification:
### The difference between sxpContextModel and MySecContextModel lies in:
### 1. MySecContextModel added section_section matrix, i.e. "c_c", to update section weight,
###    while sxpContextModel did not consider this belongingness
### 2. MySecContextModel aimed at SubSec model, i.e. the words weight are influenced by sentence, context paragraph and section,
###    while sxpContextModel aimed at SubPara model, i.e. the words weight are influenced by sentence, context, paragraph

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import sys
sys.path.append("..")
import networkx as nx
from sxpPackage import *
from cmyToolkit import *
from cmySecCEIntensity import cmySecCE

#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class conTextModel2:
    # choice: 1 means with stopwords; 2 means without stopwords
    def __init__(self, pickle_path, choice=2, iteration_times=20, opt='nonce', bias=0.5):
        self.w_s = None
        self.s_p = None
        self.p_c = None
        self.t_p = None
        self.s_t = None
        self.w = []
        self.s = []
        self.p = []
        self.c = []
        self.t = []
        self.idx_w = []
        self.idx_s = []
        self.idx_p = []
        self.idx_c = []
        self.idx_t = []
        self.times = iteration_times
        self.words = []
        self.ranked_sentences = []
        self.text = LoadSxptext(pickle_path)
        self.section2sentence_id_list = {}
        if choice == 1:
            self.get_parameters_with_stopwords()
        elif choice == 2:
            self.get_parameters_without_stopwords()
        w = matrix(random.rand(len(self.words))).T
        self.iteration(w)
        self.rank_weight(opt, bias)
        self.ordered_sentence_id_set()

    def get_parameters_with_stopwords(self):
        self.words = self.text.sentence_tfidf.word
        self.w_s = matrix(self.text.s_k.toarray()).T
        self.s_p = matrix(self.text.p_s.toarray()).T
        self.p_c = matrix(self.text.c_p.toarray()).T
        self.t_p = matrix(self.text.p_t.toarray()).T
        self.s_t = matrix(self.text.t_s.toarray()).T

    def get_parameters_without_stopwords(self):
        # -- assign values to words, w_s, s_p, p_c, c_c
        self.get_parameters_with_stopwords()
        # -- get stopwords list
        f = open(os.path.join(corpdir, 'stopwords.txt'), 'r')
        lines = f.readlines()
        f.close()
        stopwords = [line.strip() for line in lines]
        # -- strip stopwords out from self.words and self.w_s
        idx = [i for i in range(len(self.words)) if self.words[i] not in stopwords
               and re.match(r'^[a-zA-Z]+$', self.words[i]) is not None]
        new_w_s = []
        for i in idx:
            new_w_s.append(array(self.w_s[i, :]).tolist())
        new_w_s = matrix(array(new_w_s))
        new_words = [self.words[i] for i in idx]
        self.words = new_words
        self.w_s = new_w_s

    def rank_weight(self, opt, bias):
        if opt == 'sysce' or opt == 'mance':
            self.s *= 1 - bias
            cepr = self.text.ce_sys if opt == 'sysce' else self.text.ce_man
            for i in range(len(self.text.sentenceset)):
                if cepr.has_key(i):
                    self.s[i] += cepr[i] * bias
            self.s = self.normalize(self.s)
        self.idx_w = argsort(array(-self.w), axis=0)
        self.idx_s = argsort(array(-self.s), axis=0)
        self.idx_p = argsort(array(-self.p), axis=0)
        self.idx_c = argsort(array(-self.c), axis=0)
        self.idx_t = argsort(array(-self.t), axis=0)

    def ordered_sentence_id_set(self):
        self.ranked_sentences = [self.text.sentenceset[self.idx_s[(i, 0)]] for i in range(len(self.text.sentenceset))]
        sec_titles = []
        for sec in self.text.section_list:
            self.section2sentence_id_list[sec.title] = []
            sec_titles.append(sec.title)
        for sentence in self.ranked_sentences:
            section_tag = self.text.paraset[sentence.id_para].section_title
            if section_tag != '' and section_tag in sec_titles:
                self.section2sentence_id_list[section_tag].append(sentence.id)

    @staticmethod
    def normalize(w):
        assert(sum(w) > 0)
        w = w / sum(w)
        return w

    def update_sentence_weight(self, w):
        s = self.w_s.T * w
        s = self.normalize(s)
        return s

    def update_context_weigth(self, s):
        t = self.s_t.T * s
        t = self.normalize(t)
        return t

    def update_paragraph_weight(self, s):
        p = self.s_p.T * s
        p = self.normalize(p)
        return p

    def update_paragraph_weight_bycontext(self, t):
        p = self.t_p.T * t
        p = self.normalize(p)
        return p

    def update_section_weight(self, p):
        sec = self.p_c.T * p
        sec = self.normalize(sec)
        return sec

    def update_word_weight(self, w, s, p, sec):
        # w = self.w_s * s + self.w_s * self.s_p * p + self.w_s * self.s_p * self.p_c * sec  # Section model
        w = self.w_s * s + self.w_s * self.s_p * p  # Para model
        w = self.normalize(w)
        return w

    def update_word_weight_bycontext(self, w, s, t, p):
        # -- SubPara Model -- #
        w = self.w_s * s + self.w_s*self.s_t*t + self.w_s * self.s_t * self.t_p * p
        # w = self.w_s * s + self.w_s * self.s_t * self.t_p * p  # this is the mostly used one in previous experiments
        w = self.normalize(w)
        return w

    def iteration(self, w):
        for i in range(self.times):
            s = self.update_sentence_weight(w)

            t = self.update_context_weigth(s)

            p = self.update_paragraph_weight_bycontext(t)

            c = self.update_section_weight(p)

            w = self.update_word_weight_bycontext(w, s, t, p)

        self.w = w
        self.s = s
        self.p = p
        self.c = c
        self.t = t

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

    def OutputAllRankSentence(self,useabstr = 1,maxwords = -1):
        sent_txt_set = []
        for sentence in self.ranked_sentences:
            sent_txt_set.append(sentence.sentence_text)
        return sent_txt_set

#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def TestPickle():
    pk = r'E:\Programs\Eclipse\CE_relation\CEsummary\kg\pickle_CEnet1\f0001.txt_2.pk'
    model = conTextModel2(pk, opt='mance')
    topksent = 10
    tops = model.OutPutTopKSent(topksent, 1, -1)
    for idx, eachs in enumerate(tops):
        print '----------------'
        print idx, eachs

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
if __name__ == '__main__':
    TestPickle()
