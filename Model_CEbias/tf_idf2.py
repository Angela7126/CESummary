# -*- coding: UTF-8 -*-

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
class TfIdf2:
    def __init__(self, pickle_path, opt='nonce', bias=0.5):
        self.section2sentence_id_list = {}
        self.text = LoadSxptext(pickle_path)
        self.words = self.text.sentence_tfidf.word
        self.ranked_sentences = []
        self.count_words = []
        self.s = []
        self.idx_s = []
        self.get_sentence_weight()
        self.rank_sentences(opt, bias)
        self.ordered_sentence_id_set()

    def MakeCESentMatrix(self, opt):
        if opt == 'nonce':
            return
        sentences = self.text.sentenceset
        ce_matrix = np.zeros((len(sentences), len(sentences)), dtype=np.float)
        if opt == 'mance':
            ce_sidlst = self.text.mance_sent_id_dict.keys()
            CE_list = self.text.man_CE_list
        elif opt == 'sysce':
            ce_sidlst = self.text.sysce_sent_id_dict.keys()
            CE_list = self.text.sys_CE_list
        for ce in CE_list:
            for i in range(len(ce.Staglst)):
                for j in range(i + 1, len(ce.Staglst)):
                    ce_matrix[ce.Staglst[i], ce.Staglst[j]] = 0.5
                    ce_matrix[ce.Staglst[j], ce.Staglst[i]] = 0.5
        for i in range(len(ce_sidlst)):
            for j in range(i + 1, len(ce_sidlst)):
                si_txt = sentences[ce_sidlst[i]].sentence_text
                sj_txt = sentences[ce_sidlst[j]].sentence_text
                jaccard = jaccard_similarity(si_txt, sj_txt)
                ce_matrix[ce_sidlst[i], ce_sidlst[j]] += jaccard
                ce_matrix[ce_sidlst[j], ce_sidlst[i]] += jaccard
        for i in range(len(sentences)):
            if sum(ce_matrix[i]) > 0:
                ce_matrix[i] = self.normalize(ce_matrix[i])
        self.ce_s = matrix(ce_matrix)

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

    # -- normalize a vector -- #
    def normalize(self, w):
        assert(sum(w) > 0)
        w = w / sum(w)
        return w

    def rank_sentences(self, opt, bias):
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
        self.s = self.normalize(matrix(array(sentences2words)).T * e)
        if opt == 'sysce' or opt == 'mance':
            self.s *= 1 - bias
            cepr = self.text.ce_sys if opt == 'sysce' else self.text.ce_man
            for i in range(len(self.text.sentenceset)):
                if cepr.has_key(i):
                    self.s[i] += cepr[i] * bias
            self.s = self.normalize(self.s)

        # -- rank the sentence by their weight reversely and return a list of their original index --
        self.idx_s = argsort(array(-self.s), axis=0)

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
    pickle_path = r'E:\Programs\Eclipse\CE_relation\CEsummary\kg\pickle_CEnet1\f0001.txt_2.pk'
    tfidf = TfIdf2(pickle_path, opt='mance')
    # for k, v in tfidf.count_words:
    #     print v, k
    topksent = 10
    tops = tfidf.OutPutTopKSent(topksent, 1, -1)
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



