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
class GraphBased2:
    # section2sentence_id_list: stores the mapping between section_title and sentences id that belong to this section
    #                           i.e. {"1 Introduction": [8,9,10,11...21]; "2 Semantic Link":[22,23,...,31]; ...}
    # idx_s: stores the sentence idx ordered reversely by their page-rank weight.
    # text: stores the sxpText object for the paper
    def __init__(self, pickle_path, opt='nonce', bias=0.5):
        self.section2sentence_id_list = {}
        self.text = LoadSxptext(pickle_path)
        self.s = []
        self.idx_s = []
        self.ranked_sentences = []
        self.page_rank(pickle_path, opt, bias)
        self.ordered_sentence_id_set()

    # -- normalize a vector -- #
    def normalize(self, w):
        assert(sum(w) > 0)
        w = w / sum(w)
        return w

    # -- page_rank: using networkx.pagerank() to rank the graph and assign values to idx_s -- #
    def page_rank(self, pickle_path, opt, bias):
        g = create_graph(pickle_path)
        pr = nx.pagerank(g)  # pr return a dict object storing sentences's page-rank weight
        self.s = matrix(zeros(len(self.text.sentenceset))).T
        for i in range(len(self.text.sentenceset)):
            if pr.has_key(i):
                self.s[i] = pr[i]
        if opt == 'sysce' or opt == 'mance':
            self.s *= 1 - bias
            cepr = self.text.ce_sys if opt == 'sysce' else self.text.ce_man
            for i in range(len(self.text.sentenceset)):
                if cepr.has_key(i):
                    self.s[i] += cepr[i] * bias
            self.s = self.normalize(self.s)
        self.idx_s = argsort(array(-self.s), axis=0)  # order sentences' index reversely by their weight

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

    # -- return all ranked sentence_text --
    def OutputAllRankSentence(self):
        sent_txt_set = []
        for sentence in self.ranked_sentences:
            sent_txt_set.append(sentence.sentence_text)
        return sent_txt_set

# ---- create_graph: create a graph where sentences are nodes and similarity among sentences are edges weight ---- #
# Input : a pickle file path which stores a sxpText object for a paper
# Output: a len(sentence)*len(sentence) matrix, element at ith row jth column is the Jaccard distance between si and sj
def create_graph(pickle_path):
    text = LoadSxptext(pickle_path)  # read sxpText object and assign to "text"
    sentences = text.sentenceset
    g = nx.Graph()  # build a non-directed graph; ps: nx.DiGraph() build a directed graph
    # -- Add nodes --
    for sent in sentences:  # use each sentence's id as the graph node
        g.add_node(sent.id)
    # -- Add edges --
    for i in range(len(sentences)):
        for j in range(i, len(sentences)):
            jaccard = jaccard_similarity(sentences[i].sentence_text, sentences[j].sentence_text)
            if jaccard > 0:
                g.add_edge(sentences[i].id, sentences[j].id, weight=jaccard)
                g.add_edge(sentences[j].id, sentences[i].id, weight=jaccard)
    return g


#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################

def test_page_rank():
    fp = r'E:\Programs\Eclipse\CE_relation\CEsummary\kg\pickle_CEnet1\f0001.txt_2.pk'
    GS = GraphBased2(fp, opt='mance')
    # print GS.section2sentence_id_list
    # print GS.idx_s
    for text in GS.OutPutTopKSent(10):
        print '----------------'
        print text

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
def main():
    test_page_rank()

if __name__ == "__main__":
    main()
