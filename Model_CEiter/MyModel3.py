# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import sys
sys.path.append("..")
from sxpPackage import *
from cmyToolkit import *
from cmySecCEIntensity import cmySecCE

#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class MyModel3:
    # choice: 1 means with stopwords; 2 means without stopwords
    def __init__(self, pickle_path, choice=2, iteration_times=20, opt='nonce', bias=0.5):
        self.w_s = None  # word_sentence matrix
        self.s_p = None  # sentence_paragraph matrix
        self.p_c = None  # paragraph_section matrix
        self.w = []  # words weight, is a len(words) * 1 matix
        self.s = []  # sentence weight, is a len(sentences) * 1 matix
        self.p = []  # paragraph weight, is a len(paragraph) * 1 matix
        self.c = []  # section weight, is a len(section) * 1 matix
        self.idx_w = []  # words idx ordered reversely by their iterated weight, because self.w is a 2D list, idx_w is len(words)*2 matrix, each element is (row_idx, column_idx)
        self.idx_s = []  # sentence idx ordered reversely by their iterated weight. idx_s is len(sentence)*2 matrix, each element is (row_idx, column_idx)
        self.idx_p = []  # paragraph idx ordered reversely by their iterated weight. idx_p is len(paragraph)*2 matrix, each element is (row_idx, column_idx)
        self.idx_c = []  # section idx ordered reversely by their iterated weight. idx_c is len(section)*2 matrix, each element is (row_idx, column_idx)
        self.times = iteration_times
        self.words = []   # keywords list
        self.ranked_sentences = []
        self.text = LoadSxptext(pickle_path)  # sxpText object
        self.section2sentence_id_list = {}  # i.e. {"1 Introduction": [8,9,10,11...21]; "2 Semantic Link":[22,23,...,31]; ...}

        if choice == 1:
            self.get_parameters_with_stopwords()  # assign values to words, w_s, s_p, p_c
        elif choice == 2:
            self.get_parameters_without_stopwords()

        self.ce_s = self.GetCEMatrix(opt)  # Get CE sentence * sentence matrix according to opt
        w = matrix(random.rand(len(self.words))).T  # Initial words weight vector
        s = matrix(random.rand(len(self.text.sentenceset))).T
        self.iteration(w, s, opt, bias)
        self.rank_weight()  # get idx_w, idx_s, idx_p, idx_c
        self.ordered_sentence_id_set()  # assign values to section2sentence_id_list

    # -- Get CE sentence * sentence matrix according to opt --
    def GetCEMatrix(self, opt):
        if opt == 'mance':
            ce_graph = self.text.ce_s_man
        elif opt == 'sysce':
            ce_graph = self.text.ce_s_sys
        else:
            return None
        ce_matrix = np.zeros((len(self.text.sentenceset), len(self.text.sentenceset)), dtype=np.float)
        for n, nbrs in ce_graph.adjacency_iter():
            for nbr, eattr in nbrs.items():
                ce_matrix[(n, nbr)] = eattr['weight']
        return ce_matrix

    # -- get_parameters_with_stopwords: assign values to words, w_s, s_p, p_c -- #
    def get_parameters_with_stopwords(self):
        self.words = self.text.sentence_tfidf.word
        self.w_s = matrix(self.text.s_k.toarray()).T
        self.s_p = matrix(self.text.p_s.toarray()).T
        self.p_c = matrix(self.text.c_p.toarray()).T

    # -- get_parameters_without_stopwords: assign values to words, w_s, s_p, p_c and strip stopwords out-- #
    def get_parameters_without_stopwords(self):
        # -- assign values to words, w_s, s_p, p_c
        self.get_parameters_with_stopwords()
        # -- get stopwords list
        f = open(os.path.join(corpdir, 'stopwords.txt'), 'r')
        lines = f.readlines()
        f.close()
        stopwords = [line.strip() for line in lines]
        # -- strip stopwords out from self.words and self.w_s
        idx = [i for i in range(len(self.words)) if self.words[i].lower() not in stopwords
               and re.match(r'^[a-zA-Z]+$', self.words[i]) is not None]
        new_w_s = []
        for i in idx:
            new_w_s.append(array(self.w_s[i, :]).tolist())
        new_w_s = matrix(array(new_w_s))
        new_words = [self.words[i] for i in idx]
        self.words = new_words
        self.w_s = new_w_s

    # -- rank_weight: get idx_w, idx_s, idx_p, idx_c -- #
    def rank_weight(self):
        self.idx_w = argsort(array(-self.w), axis=0)
        self.idx_s = argsort(array(-self.s), axis=0)
        self.idx_p = argsort(array(-self.p), axis=0)
        self.idx_c = argsort(array(-self.c), axis=0)

    # -- ordered_sentence_id_set(): assign values to section2sentence_id_list -- #
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

    # -- normalize a vector -- #
    def normalize(self, w):
        assert(sum(w) > 0)
        w = w / sum(w)
        return w

    def update_sentence_weight_with_ce(self, w, s, bias):
        s = self.w_s.T * w * (1-bias) + self.ce_s * s * bias
        s = self.normalize(s)
        return s

    def update_sentence_weight(self, w):
        s = self.w_s.T * w
        s = self.normalize(s)
        return s

    def update_paragraph_weight(self, s):
        p = self.s_p.T * s
        p = self.normalize(p)
        return p

    def update_section_weight(self, p):
        sec = self.p_c.T * p
        sec = self.normalize(sec)
        return sec

    def update_word_weight(self, w, s, p, sec):
        # -- Section Model -- #
        # w = self.w_s * s + self.w_s * self.s_p * p + self.w_s * self.s_p * self.p_c * sec
        # -- Para Model -- #
        w = self.w_s * s + self.w_s * self.s_p * p
        w = self.normalize(w)
        return w

    def iteration(self, w, s, opt, bias):
        for i in range(self.times):
            if opt == 'mance' or opt == 'sysce':
                s = self.update_sentence_weight_with_ce(w, s, bias)
            else:
                s = self.update_sentence_weight(w)

            p = self.update_paragraph_weight(s)

            c = self.update_section_weight(p)

            w = self.update_word_weight(w, s, p, c)
        self.w = w
        self.s = s
        self.p = p
        self.c = c

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

    def OutputAllRankSentence(self, useabstr=1, maxwords=-1):
        sent_txt_set = []
        for sentence in self.ranked_sentences:
            sent_txt_set.append(sentence.sentence_text)
        return sent_txt_set

#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def TestPickle():
    pk = r'E:\Programs\Eclipse\CE_relation\CEsummary\kg\pickle_SecCE\f0001.txt_abstract.pk'
    model = MyModel3(pk, opt='mance')
    topksent = 10
    tops = model.OutPutTopKSent(topksent, 0, 500)
    for idx, eachs in enumerate(tops):
        print '----------------'
        print idx, eachs

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
if __name__ == '__main__':
    TestPickle()