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
class WordGraph2:
    def __init__(self, pickle_path, opt='nonce', bias=0.5):
        self.section2sentence_id_list = {}
        self.text = LoadSxptext(pickle_path)
        self.s = []
        self.w = []
        self.idx_s = []
        self.idx_w = []
        self.words = []
        self.ranked_sentences = []
        self.page_rank(pickle_path, opt, bias)
        self.ordered_sentence_id_set()

    # -- normalize a vector -- #
    def normalize(self, w):
        assert (sum(w) > 0)
        w = w / sum(w)
        return w

    def page_rank(self, pickle_path, opt, bias):
        g = create_graph(pickle_path)
        pr = nx.pagerank(g)
        for elem in pr.items():
            self.words.append(elem[0])
            self.w.append(elem[1])
        for sent in self.text.sentenceset:
            words = sent.sentence_text.split()
            weight = 0
            for word in words:
                word = word.lower()
                if word not in pr.keys():
                    continue
                weight += pr[word]
            self.s.append(weight)
        self.s = self.normalize(self.s)

        if opt == 'sysce' or opt == 'mance':
            self.s *= 1 - bias
            cepr = self.text.ce_sys if opt == 'sysce' else self.text.ce_man
            for i in range(len(self.text.sentenceset)):
                if cepr.has_key(i):
                    self.s[i] += cepr[i] * bias
            self.s = self.normalize(self.s)

        self.idx_s = argsort(-array(self.s)).tolist()
        self.idx_w = argsort(-array(self.w)).tolist()

    def ordered_sentence_id_set(self):
        self.ranked_sentences = [self.text.sentenceset[self.idx_s[i]]
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
# -------------------------------- Words graph building ----------------------------- #
#######################################################################################
# ---- create_graph function: ---- #
# Input: pickle file path of sxpText object; window size
# Output: a words graph: each words in the whole token list is a node, words that appear in a given window will set up a edges
# for example:
#   text = 'There was never a night or a problem that could defeat sunrise or hope.'
#   token list = ['there', 'was', 'never', 'a', 'night', 'or', 'problem', 'that', 'could', 'defeat', 'sunrise', 'hope']
#   node list = token list
#   set window size = 3
#   edges: because "There was never" appear together in text, so add edges between "there", "was", "a"; in the same way,
#          edges are also been added between "was","never","a", ...
def create_graph(pickle_path, window=3):
    text = LoadSxptext(pickle_path)
    sentences = text.sentenceset
    # -- get stopwords list --
    f = open(os.path.join(corpdir, 'stopwords.txt'), 'r')
    lines = f.readlines()
    f.close()
    stopwords = [line.strip() for line in lines]
    # -- build word network ---
    g = nx.Graph()
    for sent in sentences:
        words = sent.sentence_text.split()
        for i in range(len(words)):
            if words[i].lower() in stopwords or re.match(r'^[a-zA-Z]+$', words[i]) is None:
                continue
            for j in range(i + 1, i + window):
                if j < 0 or j >= len(words):
                    continue
                if words[j].lower() in stopwords or re.match(r'^[a-zA-Z]+$', words[j]) is None:
                    continue
                g.add_edge(words[i].lower(), words[j].lower())
    return g

#######################################################################################
# ----------------------- Some test and demonstration functions --------------------- #
#######################################################################################
def ShowRankedWords():
    pk = r'E:\Programs\Eclipse\CE_relation\CEsummary\kg\pickle_CEnet1\f0001.txt_2.pk'
    wg = WordGraph2(pk)
    sorted_word = [[wg.words[wg.idx_w[i]], wg.w[wg.idx_w[i]]]
                   for i in range(len(wg.words))]
    for word in sorted_word:
        print word

def Testread():
    pickle_path = r'E:\Programs\Eclipse\CE_relation\CEsummary\kg\pickle_CEnet1\f0001.txt_2.pk'
    sxptxt = LoadSxptext(pickle_path)
    print sxptxt.sentence_tfidf.word


def TestPickle():
    pk = r'E:\Programs\Eclipse\CE_relation\CEsummary\kg\pickle_CEnet1\f0001.txt_2.pk'
    model = WordGraph2(pk,opt='mance')
    topksent = 15
    tops = model.OutPutTopKSent(topksent, 1, -1)
    for i, eachs in enumerate(tops):
        print '----------------'
        print i, eachs

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
def main():
    TestPickle()
    # ShowRankedWords()

if __name__ == '__main__':
    main()
