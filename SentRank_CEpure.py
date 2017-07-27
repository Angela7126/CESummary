# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
from Model_CEfliter.graph_base import GraphBased
from Model_CEfliter.MyModel import MyModel
from Model_CEfliter.MySecContextModel import SecConTextModel
from Model_CEfliter.MySecModel import MySecModel
from Model_CEfliter.MySecTitleNetwork import MySecTitleModel
from Model_CEfliter.sxpContextModel import conTextModel
from Model_CEfliter.sxpHybridGraph import HybridGraph
from Model_CEfliter.tf_idf import TfIdf
from Model_CEfliter.word_graph import WordGraph
from cmyToolkit import *
from cmyDoTestPyrouge import *

# ------------ some dict object ---------------
idname = {'cepure_man':'00', 'mymodel': '01', 'tfidf': '02', 'graphb': '03', 'graphw': '04', 'context1': '05', 'mysecmodel': '06',
           'myseccontextmodel': '07', 'hybrid': '08', 'sectitle': '09', 'cepure_sys':'10'}


#######################################################################################
# --------------------------------- Write html files  ------------------------------- #
#######################################################################################
def ProduceSystem(tops, fn, formatsent=0):
    modeltxt = '''<html>\n<head>\n<title>%s</title>\n</head>\n''' % (fn)
    # ---- get sentences list ----
    if type(tops) != list:
        if type(tops) != str and type(tops) != unicode:
            if formatsent == 1:
                return modeltxt
            else:
                return ""
        tops = re.split("(?<=[\.|?|!|;|:])[ |\"]+", tops.strip())
    # ---- change sentences into some format ----
    abstract_str = ''
    for i, sent in enumerate(tops):
        rsent = RemoveUStrSpace(sent)
        if len(rsent) <= 0:
            rsent = 'test sentence is empty'
        if formatsent == 1:
            sentr = '''<a name="%d">[%d]</a> <a href="#%d" id=%d>%s</a>\n''' % (i, i, i, i, rsent)
        if formatsent == 0:
            sentr = rsent + '\n'
        abstract_str += sentr
    # ---- get body text ----
    if formatsent == 1:
        bodytxt = '''<body bgcolor="white">\n%s</body>\n</html>''' % (abstract_str)
    if formatsent == 0:
        bodytxt = abstract_str
    # ---- get whole text and return ----
    if formatsent == 1:
        abstract_str = modeltxt + bodytxt
    if formatsent == 0:
        abstract_str = bodytxt
    return abstract_str


#######################################################################################
# ---------------------- Choose model to rank and save result ----------------------- #
#######################################################################################
def OutPutTopKmanCESent(sxptxt, topk, useabstr = 1, maxwords = -1):
    if len(sxptxt.man_CE_list) == 0:
        return []
    ranked_sentences = sorted(sxptxt.ce_man.iteritems(), key=lambda asd:asd[1], reverse=True)
    i = 0  # i stores how many sentences have been append into sent_txt_set
    wordlen = 0  # wordlen stores how many str has been append into sent_txt_set
    # useabstr == 1, use number of str in abstract as the maxwords
    if useabstr == 1:
        abstractlen = len(sxptxt.abstract)
    # useabstr == 2, use number of str in conclusion as the maxwords
    elif useabstr == 2:
        abstractlen = len(sxptxt.conclusion)
    # useabstr == 3, use number of str in abstract and conclusion as the maxwords
    else:
        abstractlen = len(sxptxt.abstract) + len(sxptxt.conclusion)
    # -- get top k sentence --
    sent_txt_set = []
    for sentid in ranked_sentences:
        if i >= topk and maxwords == 0:  # maxwords == 0 means use topk sentence as upper bound
            break
        if wordlen >= abstractlen and maxwords == -1:  # maxwords == 1 means use abstractlen str as upper found
            break
        senttxt = sxptxt.sentenceset[sentid[0]].sentence_text
        if len(senttxt) <= 1:  # ignore sentence that contains less than 2 str
            continue
        sent_txt_set.append(senttxt)
        wordlen += len(senttxt)
        i += 1
    return sent_txt_set


def OutPutTopKsysCESent(sxptxt, topk, useabstr=1, maxwords=-1):
    if len(sxptxt.sys_CE_list) == 0:
        return []
    ranked_sentences = sorted(sxptxt.ce_sys.iteritems(), key=lambda asd:asd[1], reverse=True)
    i = 0  # i stores how many sentences have been append into sent_txt_set
    wordlen = 0  # wordlen stores how many str has been append into sent_txt_set
    # useabstr == 1, use number of str in abstract as the maxwords
    if useabstr == 1:
        abstractlen = len(sxptxt.abstract)
    # useabstr == 2, use number of str in conclusion as the maxwords
    elif useabstr == 2:
        abstractlen = len(sxptxt.conclusion)
    # useabstr == 3, use number of str in abstract and conclusion as the maxwords
    else:
        abstractlen = len(sxptxt.abstract) + len(sxptxt.conclusion)
    # -- get top k sentence --
    sent_txt_set = []
    for sentid in ranked_sentences:
        if i >= topk and maxwords == 0:  # maxwords == 0 means use topk sentence as upper bound
            break
        if wordlen >= abstractlen and maxwords == -1:  # maxwords == 1 means use abstractlen str as upper found
            break
        senttxt = sxptxt.sentenceset[sentid[0]].sentence_text
        if len(senttxt) <= 1:  # ignore sentence that contains less than 2 str
            continue
        sent_txt_set.append(senttxt)
        wordlen += len(senttxt)
        i += 1
    return sent_txt_set


def GetComparingText(fp, papers_path, pk_path, useabstr=1, fname_topk_dict={}):
    # -- create the directory which store the comparing text serve as manual summary for each paper --
    txt_dir = os.path.join(fp, 'model_html')
    if not os.path.exists(txt_dir):
        os.makedirs(txt_dir)

    # -- get the original filename list in the path variable --
    file_list = sxpGetDirFileList(papers_path)[0]

    # -- pickle_dir is the directory which store sxpText object pickle file --
    pickle_dir = pk_path

    # --  get sxpText objects --
    for i, file_name in enumerate(file_list):
        fset = file_name.split('.')
        if fset[-1] not in ['txt', 'xhtml']:  # if current file is not a txt file, it is not one of the original papers
            continue
        print "getting ", i, "th paper's comparing text named as", file_name, "type = ", useabstr
        # -- get single pickle file directory --
        pickle_path = os.path.join(pickle_dir, file_name + '_2.pk')
        sxptxt = LoadSxptext(pickle_path)
        # -- save text abstact text and conclusion text --
        # get comparing text
        useabstr = useabstr if useabstr <= 3 else 3
        comptxt_dir = os.path.join(txt_dir,  file_name+'.'+["C","A","B","C"][useabstr]+'.html')
        if useabstr == 1:
            comptxt = sxptxt.abstract
        elif useabstr == 2:
            comptxt = sxptxt.conclusion
        else:
            comptxt = sxptxt.abstract + ' ' + sxptxt.conclusion
        # split the comparing text into sentences by "**." and delete empty sentences
        comptxtlst = DelEmptyString((comptxt.strip()+'\n').split('**.\n'))
        if len(comptxtlst) == 0:
            continue
        # create file content and write file
        ct = ProduceSystem(comptxtlst, file_name, 1)
        WriteStrFile(comptxt_dir, ct, 'utf-8')
        if fname_topk_dict.has_key(file_name):
            fname_topk_dict[file_name].append(len(comptxtlst))
        else:
            fname_topk_dict[file_name] = [len(comptxtlst)]
    print "Prepare comparing text complete"
    return fname_topk_dict


# ---- evaluate_one_model function : ---- #
# Input:
#   1. pickle_path: the directory path that stores all sxpText pickle files for test papers
#   2. system_path: the directory path where you want to save the model's top k sentences as the system_summary result
#   3. pk_sys_set: is a 2D list, each element is a pair like [file_name, system_name]
#                  file_name: the sxpText pickle file name
#                  system_name: the file name that you want to save the top k sentences
#   4. system_id: the id of model, see test.py idname dict's values
#   5. modeltype: the name of model, see test.py idname dict's keys, defaulted as 'mymodel'
#   6. topksent: the top k sentences that you want to use for evaluation, defaulted as 10
# Output:
#   save the top k sentences in a text file at system_path + system_name + system_id
#   save all ranked sentences in a pickle file at system_path + system_name + system_id + "allsent.pk"
def evaluate_one_model(pickle_path, pk_sys_set, system_path, system_id, modeltype='mymodel', topksent=10, on_mance=False, on_sysce=False):
    print "model type =", modeltype, "top k =", topksent
    for i, (file_name, system_name) in enumerate(pk_sys_set):
        print i, file_name
        pickle_file = os.path.join(pickle_path, file_name)
        if modeltype == 'mymodel':  # MyModel.py
            model = MyModel(pickle_file)
        if modeltype == 'tfidf':  # tf_idf.py
            model = TfIdf(pickle_file)
        if modeltype == 'graphb':  # graph_base.py
            model = GraphBased(pickle_file)
        if modeltype == 'graphw':  # word_graph.py
            model = WordGraph(pickle_file)
        if modeltype == 'context1':  # sxpContextModel.py  SubPara Model
            model = conTextModel(pickle_file)
        if modeltype == 'mysecmodel':  # MySecModel.py
            model = MySecModel(pickle_file)
        if modeltype == 'myseccontextmodel':  # MySecContextModel.py SecSub Model
            model = SecConTextModel(pickle_file)
        if modeltype == 'hybrid':  # sxpHybridGraph.py
            model = HybridGraph(pickle_file)
        if modeltype == 'sectitle':  # MySecTitleNetwork.py
            model = MySecTitleModel(pickle_file)
        # -- save top k sentences to text --
        topksent_path = os.path.join(system_path, system_name + "." + system_id + ".txt")
        tops = model.OutPutTopKSent(topksent, 1, -1)
        st = ProduceSystem(tops, file_name, 1)
        WriteStrFile(topksent_path, st, 'utf-8')
        if on_mance:
            topk_mance_sent_path = os.path.join(system_path, system_name + "." + system_id + ".mance.txt")
            topk_mance_sent = OutPutTopKmanCESent(model, topksent, 1, -1)
            mance_st = ProduceSystem(topk_mance_sent, file_name, 1)
            WriteStrFile(topk_mance_sent_path, mance_st, 'utf-8')
        if on_sysce:
            topk_sysce_sent_path = os.path.join(system_path, system_name+"."+system_id+".sysce.txt")
            topk_sysce_sent = OutPutTopKsysCESent(model, topksent, 1, -1)
            sysce_st = ProduceSystem(topk_sysce_sent, file_name, 1)
            WriteStrFile(topk_sysce_sent_path, sysce_st, 'utf-8')
        # -- save all ranked sentences to text --
        allsent = model.OutputAllRankSentence()
        pkfname = topksent_path + 'allsent.pk'
        StoreSxptext(allsent, pkfname)
        i += 1
    print "ranking complete!"


# ---- evaluate_all: ---- #
# Input:
#   1. fp: the sxpText object pickles directory
#   2. modeltype: a string belongs to ['mymodel', 'tfidf', 'graphb', 'graphw', 'context1', 'mysecmodel', 'myseccontextmodel', 'hybird', 'sectitle']
#   3. topksent: the number of sentences that you want to produced as a summary, default as 10
#   4. useabstr: belongs to [1,2,3], indicate the comparing text type
#               useabstr = 1: use abstract as comparing text
#               useabstr = 2: use conclusion as comparing text
#               useabstr = 3: use abstract + conclusion as comparing text
#   5. maxtxt: belongs to [-1, 0], used as a parameter in output top k sentence:
#               maxtxt = -1 means the length of str in output sentence set is upper bounded by the length of str in its abstraction or conclusion
#               maxtxt = 0 means the number of output sentences is upper bounded by input topksent
#   6. inc_abscon: a bool variable, indicate check the sxpText add abs&conc in its paragraph and sentence set or not added, default as True
# Output:
#   1. store each model's topk sentence as a html file
#   2. same each paper's abstract or conclusion or abstract + conclusion as a html file which serves as comparing text
def evaluate_all_kg(fp, papers_path, pk_path, modeltype='mymodel', inc_abscon=True, useabstr=1, maxtxt=-1, fname_topk_dict={}):
    print "model type =", modeltype
    # systemdir should be managed accoding to the inc_abscon parameter
    if not inc_abscon:
        system_dir = os.path.join(fp, 'systemPure_1')
        system_mandir = os.path.join(fp, 'systemPure_man1')
    else:
        system_dir = os.path.join(fp, 'systemPure_2')
        system_mandir = os.path.join(fp, 'systemPure_man2')
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)
    if not os.path.exists(system_mandir):
        os.makedirs(system_mandir)

    # -- get the original filename list in the path variable --
    file_list = sxpGetDirFileList(papers_path)[0]

    # -- for each file, get its sxpText and run modeltype ranking model on it --
    for i, file_name in enumerate(file_list):
        # ---- get topk sentence ----
        if not fname_topk_dict.has_key(file_name):
            continue
        else:
            topk = fname_topk_dict[file_name]
        # ---- get file name ----
        fset = file_name.split('.')
        if fset[-1] != 'txt':  # if current file is not a txt file, it is not one of the original papers
            continue
        print "processing", i, "th paper named as", file_name
        # -- get single pickle file directory --
        if not inc_abscon:
            pickle_path = os.path.join(pk_path, file_name + '_1.pk')
        else:
            pickle_path = os.path.join(pk_path, file_name + '_2.pk')
        # -- run ranking model on sxpText object at pickle_path --
        if modeltype == 'mymodel':
            model = MyModel(pickle_path)
        if modeltype == 'tfidf':
            model = TfIdf(pickle_path)
        if modeltype == 'graphb':
            model = GraphBased(pickle_path)
        if modeltype == 'graphw':
            model = WordGraph(pickle_path)
        if modeltype == 'context1':
            model = conTextModel(pickle_path)
        if modeltype == 'mysecmodel':
            model = MySecModel(pickle_path)
        if modeltype == 'myseccontextmodel':
            model = SecConTextModel(pickle_path)
        if modeltype == 'hybrid':  # sxpHybridGraph.py
            model = HybridGraph(pickle_path)
        if modeltype == 'sectitle':  # MySecTitleNetwork.py
            model = MySecTitleModel(pickle_path)

        # -- get the .html file's suffix NO. --
        if modeltype in idname.keys():
            idstr = idname[modeltype]
        # -- save original model ranked topk sentences to text --
        tops = model.OutPutTopKSent(topk, useabstr, maxtxt)
        st = ProduceSystem(tops, file_name, 1)
        topksent_path = os.path.join(system_dir, file_name+'.html.'+idstr)
        WriteStrFile(topksent_path, st, 'utf-8')
        topksent_path = os.path.join(system_mandir, file_name + '.html.' + idstr)
        WriteStrFile(topksent_path, st, 'utf-8')
    print "ranking complete"


def CEPureRankedSentKG(fp, papers_path, pk_path, inc_abscon=True, useabstr=1, maxtxt=-1, fname_topk_dict={}):
    print "model type = CEpure"
    if not inc_abscon:
        system_dir = os.path.join(fp, 'systemPure_1')
        system_mandir = os.path.join(fp, 'systemPure_man1')
    else:
        system_dir = os.path.join(fp, 'systemPure_2')
        system_mandir = os.path.join(fp, 'systemPure_man2')
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)
    if not os.path.exists(system_mandir):
        os.makedirs(system_mandir)

    # -- get the original filename list in the path variable --
    file_list = sxpGetDirFileList(papers_path)[0]

    for i, file_name in enumerate(file_list):
        # ---- get topk sentence ----
        if not fname_topk_dict.has_key(file_name):
            continue
        else:
            topk = fname_topk_dict[file_name]
        # ---- get file name ----
        fset = file_name.split('.')
        if fset[-1] != 'txt':  # if current file is not a txt file, it is not one of the original papers
            continue
        print "processing", i, "th paper named as", file_name
        # -- get single pickle file directory --
        if not inc_abscon:
            pickle_path = os.path.join(pk_path, file_name + '_1.pk')
        else:
            pickle_path = os.path.join(pk_path, file_name + '_2.pk')
        sxptxt = LoadSxptext(pickle_path)
        # -- Output TopK manual CE sentences --
        topksent_path = os.path.join(system_mandir, file_name + '.html.' + idname['cepure_man'])
        tops = OutPutTopKmanCESent(sxptxt, topk, useabstr, maxtxt)
        if len(tops) > 0:
            st = ProduceSystem(tops, file_name, 1)
            WriteStrFile(topksent_path, st, 'utf-8')
        # -- Output TopK auto-extracted CE sentences --
        topksent_path = os.path.join(system_dir, file_name + '.html.' + idname['cepure_sys'])
        tops = OutPutTopKsysCESent(sxptxt, topk, useabstr, maxtxt)
        if len(tops) > 0:
            st = ProduceSystem(tops, file_name, 1)
            WriteStrFile(topksent_path, st, 'utf-8')
    print "ranking complete"


def evaluate_all_acl(fp, papers_path, pk_path, modeltype='mymodel', inc_abscon=True, useabstr=1, maxtxt=-1, topk=10):
    print "model type =", modeltype
    # -- if modeltype is not in our model list, not execute the following process --
    if modeltype not in idname.keys():
        return
    # -- get algorithms generated summaries directory --
    if not inc_abscon:
        system_dir = os.path.join(fp, 'systemPure_html1')
        rankedsentdir = os.path.join(fp, 'RankedSentPure_1')
    else:
        system_dir = os.path.join(fp, 'systemPure_html2')
        rankedsentdir = os.path.join(fp, 'RankedSentPure_2')
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)
    if not os.path.exists(rankedsentdir):
        os.makedirs(rankedsentdir)

    # -- get the original filename list in the path variable --
    file_list = sxpGetDirFileList(papers_path)[0]

    # -- for each file, get its sxpText and run modeltype ranking model on it --
    for i, file_name in enumerate(file_list):
        # ---- get file name ----
        fset = file_name.split('.')
        if fset[-1] != 'xhtml':  # if current file is not a txt file, it is not one of the original papers
            continue
        print "processing", i, "th paper named as", file_name
        # -- get single pickle file directory --
        if not inc_abscon:
            pickle_path = os.path.join(pk_path, file_name +'_1.pickle')
        else:
            pickle_path = os.path.join(pk_path, file_name +'_2.pickle')
        # -- run ranking model on sxpText object at pickle_path --
        if modeltype == 'mymodel':
            model = MyModel(pickle_path)
        if modeltype == 'tfidf':
            model = TfIdf(pickle_path)
        if modeltype == 'graphb':
            model = GraphBased(pickle_path)
        if modeltype == 'graphw':
            model = WordGraph(pickle_path)
        if modeltype == 'context1':
            model = conTextModel(pickle_path)
        if modeltype == 'mysecmodel':
            model = MySecModel(pickle_path)
        if modeltype == 'myseccontextmodel':
            model = SecConTextModel(pickle_path)
        if modeltype == 'hybrid':  # sxpHybridGraph.py
            model = HybridGraph(pickle_path)
        if modeltype == 'sectitle':  # MySecTitleNetwork.py
            model = MySecTitleModel(pickle_path)

        # -- get the .html file's suffix NO. --
        idstr = idname[modeltype]
        # -- save ranked sentence to a pickle file --
        ranked_sent_fp = os.path.join(rankedsentdir, file_name+".html."+idstr+".allsent.pk")
        sentidlst = sorted(model.text.ce_sys.iteritems(), key=lambda asd:asd[1], reverse=True)
        ranked_sentences = [model.text.sentenceset[sentid[0]].sentence_text for sentid in sentidlst]
        StoreSxptext(ranked_sentences, ranked_sent_fp)
        # -- save original model ranked topk sentences to text --
        topksent_path = os.path.join(system_dir, file_name+'.html.'+idstr)
        tops = model.OutPutTopKSent(topk, useabstr, maxtxt)
        st = ProduceSystem(tops, file_name, 1)
        WriteStrFile(topksent_path, st, 'utf-8')
    print "ranking complete"


def CEPureRankedSentACL(fp, papers_path, pk_path, inc_abscon=True, useabstr=1, maxtxt=-1, topk=10):
    print "model type = CEpure"
    if not inc_abscon:
        system_dir = os.path.join(fp, 'systemPure_html1')
        rankedsentdir = os.path.join(fp, 'RankedSentPure_1')
    else:
        system_dir = os.path.join(fp, 'systemPure_html2')
        rankedsentdir = os.path.join(fp, 'RankedSentPure_2')
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)
    if not os.path.exists(rankedsentdir):
        os.makedirs(rankedsentdir)

    # -- get the original filename list in the path variable --
    file_list = sxpGetDirFileList(papers_path)[0]

    for i, file_name in enumerate(file_list):
        # ---- get file name ----
        fset = file_name.split('.')
        if fset[-1] != 'xhtml':  # if current file is not a txt file, it is not one of the original papers
            continue
        print "processing", i, "th paper named as", file_name
        # -- get single pickle file directory --
        if not inc_abscon:
            pickle_path = os.path.join(pk_path, file_name + '_1.pickle')
        else:
            pickle_path = os.path.join(pk_path, file_name + '_2.pickle')
        sxptxt = LoadSxptext(pickle_path)
        # -- save ranked sentence to a pickle file --
        ranked_sent_fp = os.path.join(rankedsentdir, file_name + ".html." + idname['cepure_sys'] + ".allsent.pk")
        sentidlst = sorted(sxptxt.ce_sys.iteritems(), key=lambda asd: asd[1], reverse=True)
        ranked_sentences = [sxptxt.sentenceset[sentid[0]].sentence_text for sentid in sentidlst]
        StoreSxptext(ranked_sentences, ranked_sent_fp)
        # -- Output TopK auto-extracted CE sentences --
        topksent_path = os.path.join(system_dir, file_name + '.html.' + idname['cepure_sys'])
        tops = OutPutTopKsysCESent(sxptxt, topk, useabstr, maxtxt)
        if len(tops) > 0:
            st = ProduceSystem(tops, file_name, 1)
            WriteStrFile(topksent_path, st, 'utf-8')
    print "ranking complete"


def evaluate_all_duc(fp, papers_path, pk_path, modeltype='mymodel', inc_abscon=True, useabstr=1, maxtxt=-1, topk=10):
    print "model type =", modeltype
    # -- if modeltype is not in our model list, not execute the following process --
    if modeltype not in idname.keys():
        return
    # -- get algorithms generated summaries directory --
    if not inc_abscon:
        system_dir = os.path.join(fp, 'systemPure_html1')
        rankedsentdir = os.path.join(fp, 'RankedSentPure_1')
    else:
        system_dir = os.path.join(fp, 'systemPure_html2')
        rankedsentdir = os.path.join(fp, 'RankedSentPure_2')
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)
    if not os.path.exists(rankedsentdir):
        os.makedirs(rankedsentdir)

    # -- get the original filename list in the path variable --
    file_list = sxpGetDirFileList(papers_path)[0]

    # -- for each file, get its sxpText and run modeltype ranking model on it --
    for i, file_name in enumerate(file_list):
        # ---- get file name ----
        if not re.match(ur'AP\d{6}-\d{4}|FBIS\d-\d+', file_name):  # if current file is not one of the original papers
            continue
        print "processing", i, "th paper named as", file_name
        # -- get single pickle file directory --
        if not inc_abscon:
            pickle_path = os.path.join(pk_path, file_name)
        else:
            pickle_path = os.path.join(pk_path, file_name)
        # -- run ranking model on sxpText object at pickle_path --
        if modeltype == 'mymodel':
            model = MyModel(pickle_path)
        if modeltype == 'tfidf':
            model = TfIdf(pickle_path)
        if modeltype == 'graphb':
            model = GraphBased(pickle_path)
        if modeltype == 'graphw':
            model = WordGraph(pickle_path)
        if modeltype == 'context1':
            model = conTextModel(pickle_path)
        if modeltype == 'mysecmodel':
            model = MySecModel(pickle_path)
        if modeltype == 'myseccontextmodel':
            model = SecConTextModel(pickle_path)
        if modeltype == 'hybrid':  # sxpHybridGraph.py
            model = HybridGraph(pickle_path)
        if modeltype == 'sectitle':  # MySecTitleNetwork.py
            model = MySecTitleModel(pickle_path)

        # -- get the .html file's suffix NO. --
        idstr = idname[modeltype]
        # -- save ranked sentence to a pickle file --
        ranked_sent_fp = os.path.join(rankedsentdir, file_name + ".html." + idstr + ".allsent.pk")
        sentidlst = sorted(model.text.ce_sys.iteritems(), key=lambda asd: asd[1], reverse=True)
        ranked_sentences = [model.text.sentenceset[sentid[0]].sentence_text for sentid in sentidlst]
        StoreSxptext(ranked_sentences, ranked_sent_fp)
        # -- save original model ranked topk sentences to text --
        topksent_path = os.path.join(system_dir, file_name+'.html.'+idstr)
        tops = model.OutPutTopKSent(topk, useabstr, maxtxt)
        st = ProduceSystem(tops, file_name, 1)
        WriteStrFile(topksent_path, st, 'utf-8')
    print "ranking complete"


def CEPureRankedSentDUC(fp, papers_path, pk_path, inc_abscon=True, useabstr=1, maxtxt=-1, topk=10):
    print "model type = CEpure"
    if not inc_abscon:
        system_dir = os.path.join(fp, 'systemPure_html1')
        rankedsentdir = os.path.join(fp, 'RankedSentPure_1')
    else:
        system_dir = os.path.join(fp, 'systemPure_html2')
        rankedsentdir = os.path.join(fp, 'RankedSentPure_2')
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)
    if not os.path.exists(rankedsentdir):
        os.makedirs(rankedsentdir)

    # -- get the original filename list in the path variable --
    file_list = sxpGetDirFileList(papers_path)[0]

    for i, file_name in enumerate(file_list):
        # ---- get file name ----
        if not re.match(ur'AP\d{6}-\d{4}|FBIS\d-\d+', file_name):  # if current file is not one of the original papers
            continue
        print "processing", i, "th paper named as", file_name
        # -- get single pickle file directory --
        if not inc_abscon:
            pickle_path = os.path.join(pk_path, file_name)
        else:
            pickle_path = os.path.join(pk_path, file_name)
        sxptxt = LoadSxptext(pickle_path)
        # -- save ranked sentence to a pickle file --
        ranked_sent_fp = os.path.join(rankedsentdir, file_name + ".html." + idname['cepure_sys'] + ".allsent.pk")
        sentidlst = sorted(sxptxt.ce_sys.iteritems(), key=lambda asd: asd[1], reverse=True)
        ranked_sentences = [sxptxt.sentenceset[sentid[0]].sentence_text for sentid in sentidlst]
        StoreSxptext(ranked_sentences, ranked_sent_fp)
        # -- Output TopK auto-extracted CE sentences --
        topksent_path = os.path.join(system_dir, file_name + '.html.' + idname['cepure_sys'])
        tops = OutPutTopKsysCESent(sxptxt, topk, useabstr, maxtxt)
        if len(tops) > 0:
            st = ProduceSystem(tops, file_name, 1)
            WriteStrFile(topksent_path, st, 'utf-8')
    print "ranking complete"

#######################################################################################
# ------- evaluate ranking result by human labeled sentence in introduction --------- #
#######################################################################################
# ---- evaluate: evaluate ranking result by human labeled sentence in introduction ----
# Input:
#   1. intro_id_list: a list record the sentences id that are in top k and also in introduction
#   2. intro_labeled_id_set: a list record sentences that manual labeled in introduction that are viewed as important sentences
#   3. choice: the evaluation metrics, default as 1
#           choice = 1: precision + recall on the whole intro_id_list
#           choice = 2: precision on the beginning len(intro_labeled_id_set) sentences of intro_id_list
# Output:
#   precision + recall   ||   precision
def evaluate(intro_id_list, intro_labeled_id_set, choice=1):
    if len(intro_id_list) == 0:
        print "no introduction"
        return -1
    if choice == 1:
        return top_k_precision_and_recall(15, intro_id_list, intro_labeled_id_set)
    elif choice == 2:
        return precision(intro_id_list, intro_labeled_id_set)


# ---- evaluate the top k sentence's precision and recall on human labeled sentences on introduction ----
def top_k_precision_and_recall(k, intro_id_list, intro_labeled_id_set):
    size = len(intro_id_list) if len(intro_id_list) < k else k
    common_ids = set(intro_labeled_id_set).intersection(set(intro_id_list[:size]))
    pre = float(len(common_ids)) / size
    recall = float(len(common_ids)) / len(intro_labeled_id_set)
    if pre == 0 or recall == 0:
        f_score = 0
    else:
        f_score = pre * recall / float(pre + recall)
    return pre, recall, f_score


# ---- evaluate the precision on the beginning len(intro_labeled_id_set) sentences of intro_id_list ----
def precision(intro_id_list, intro_label_id_set):
    size = len(intro_label_id_set)
    top_k = intro_id_list[:size]
    common_ids = set(intro_label_id_set).intersection(set(top_k))
    return len(common_ids) / float(size)


#######################################################################################
# ------------------- ranking sentences and create pickle files --------------------- #
#######################################################################################
def RankOnKG_GetModSysFiles(path, papers_path, pk_path, maxwords = 0, topksents=10):
    # ---- Prepare comparing text ----
    # fname_topk_dict = {}
    # for abscon in [1,2,3]:
    #     fname_topk_dict = GetComparingText(path, papers_path, pk_path, abscon, fname_topk_dict)
    # for key in fname_topk_dict.keys():
    #     fname_topk_dict[key] = sum(fname_topk_dict[key])/len(fname_topk_dict[key])
    # Dumppickle(os.path.join(DICpkdir, 'KGpaper_topk_dict.pk'), fname_topk_dict)
    fname_topk_dict = Loadpickle(os.path.join(DICpkdir, 'KGpaper_topk_dict.pk'))
    useabscon = 1
    # # ---- in_abscon determines whether abstraction and conclusion sentence in ranking process ----
    for inc_abscon in [True, False]:
        evaluate_all_kg(path, papers_path, pk_path, 'mymodel', inc_abscon, useabscon, maxwords,  fname_topk_dict)
        evaluate_all_kg(path, papers_path, pk_path, 'tfidf', inc_abscon, useabscon, maxwords,  fname_topk_dict)
        evaluate_all_kg(path, papers_path, pk_path, 'graphb', inc_abscon, useabscon, maxwords,  fname_topk_dict)
        evaluate_all_kg(path, papers_path, pk_path, 'graphw', inc_abscon, useabscon, maxwords,  fname_topk_dict)
        evaluate_all_kg(path, papers_path, pk_path, 'context1', inc_abscon, useabscon, maxwords,  fname_topk_dict)
        evaluate_all_kg(path, papers_path, pk_path, 'mysecmodel', inc_abscon, useabscon, maxwords,  fname_topk_dict)
        evaluate_all_kg(path, papers_path, pk_path, 'myseccontextmodel', inc_abscon, useabscon, maxwords,  fname_topk_dict)
        evaluate_all_kg(path, papers_path, pk_path, 'hybrid', inc_abscon, useabscon, maxwords,  fname_topk_dict)
        evaluate_all_kg(path, papers_path, pk_path, 'sectitle', inc_abscon, useabscon, maxwords,  fname_topk_dict)
        CEPureRankedSentKG(path, papers_path, pk_path, inc_abscon, useabscon, maxwords, fname_topk_dict)
    model_path = os.path.join(path, 'model_html')
    system_dir = ['systemPure_man1', 'systemPure_man2', 'systemPure_1', 'systemPure_2']
    system_idlst = [
        ['01', '02', '03', '04', '05', '06', '07', '08', '09', '00'],
        ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']]
    TestCallKG(path, model_path, system_dir, system_idlst)


def RankOnACL_GetModSysFiles(path, papers_path, pk_path, maxwords=-1, topksents=10):
    # ---- Prepare comparing text ----
    # for abscon in [1,2]:
    #     GetComparingText(path, papers_path, pk_path, abscon)
    useabscon = 1
    # # # ---- in_abscon determines whether abstraction and conclusion sentence in ranking process ----
    # for inc_abscon in [True, False]:
    #     evaluate_all_acl(path, papers_path, pk_path, 'mymodel', inc_abscon, useabscon, maxwords, topksents)
    #     evaluate_all_acl(path, papers_path, pk_path, 'tfidf', inc_abscon, useabscon, maxwords, topksents)
    #     evaluate_all_acl(path, papers_path, pk_path, 'graphb', inc_abscon, useabscon, maxwords, topksents)
    #     evaluate_all_acl(path, papers_path, pk_path, 'graphw', inc_abscon, useabscon, maxwords, topksents)
    #     evaluate_all_acl(path, papers_path, pk_path, 'context1', inc_abscon, useabscon, maxwords, topksents)
    #     evaluate_all_acl(path, papers_path, pk_path, 'mysecmodel',inc_abscon, useabscon, maxwords, topksents)
    #     evaluate_all_acl(path, papers_path, pk_path, 'myseccontextmodel', inc_abscon, useabscon, maxwords, topksents)
    #     evaluate_all_acl(path, papers_path, pk_path, 'hybrid', inc_abscon, useabscon, maxwords, topksents)
    #     evaluate_all_acl(path, papers_path, pk_path, 'sectitle', inc_abscon, useabscon, maxwords, topksents)
    #     CEPureRankedSentACL(path, papers_path, pk_path, inc_abscon, useabscon, maxwords, topksents)
    model_path = os.path.join(acl_dir, 'model_html')
    system_dir = ['systemPure_html1', 'systemPure_html2']
    system_idlst = [['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']]
    TestCallACL(model_path, system_dir, system_idlst)


def RankOnDUC_GetModSysFiles(path,  papers_path, pk_path, maxwords=-1, topksents=10):
    # ---- Prepare comparing text ----
    # for abscon in [1,2]:
    #    GetComparingText(path, papers_path, pk_path, abscon)
    useabscon = 1
    # # # ---- in_abscon determines whether abstraction and conclusion sentence in ranking process ----
    for inc_abscon in [True, False]:
        evaluate_all_duc(path, papers_path, pk_path, 'mymodel', inc_abscon, useabscon, 100, topksents)
        evaluate_all_duc(path, papers_path, pk_path, 'tfidf', inc_abscon, useabscon, 100, topksents)
        evaluate_all_duc(path,  papers_path, pk_path, 'graphb', inc_abscon, useabscon, maxwords, topksents)
        evaluate_all_duc(path,  papers_path, pk_path, 'graphw', inc_abscon, useabscon, maxwords, topksents)
        evaluate_all_duc(path,  papers_path, pk_path, 'context1', inc_abscon, useabscon, maxwords, topksents)
        evaluate_all_duc(path,  papers_path, pk_path, 'mysecmodel',inc_abscon, useabscon, maxwords, topksents)
        evaluate_all_duc(path,  papers_path, pk_path, 'myseccontextmodel', inc_abscon, useabscon, maxwords, topksents)
        evaluate_all_duc(path,  papers_path, pk_path, 'hybrid', inc_abscon, useabscon, maxwords, topksents)
        evaluate_all_duc(path,  papers_path, pk_path, 'sectitle', inc_abscon, useabscon, maxwords, topksents)
        CEPureRankedSentDUC(path, papers_path, pk_path, inc_abscon, useabscon, maxwords, topksents)
    model_path = os.path.join(duc_dir, 'model_html')
    system_dir = ['systemPure_html1', 'systemPure_html2']
    system_idlst = [['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']]
    TestCallDUC(model_path, system_dir, system_idlst)


#######################################################################################
# ---------------------------------- Main function ---------------------------------- #
#######################################################################################
def main():
    test = 'cedense'
    if test == 'kg':
        pk_path = os.path.join(kg_dir, 'pickle_CEnet1')
        papers_path = os.path.join(kg_dir, 'files')
        RankOnKG_GetModSysFiles(kg_dir, papers_path, pk_path, 0)
    if test == 'acl':
        pk_path = os.path.join(acl_dir, 'pickle_CEnet1')
        papers_path = os.path.join(acl_dir, 'files')
        RankOnACL_GetModSysFiles(acl_dir, papers_path, pk_path, -1, 10)
    if test == 'duc':
        pk_path = os.path.join(duc_dir, 'pickle_CEnet1')
        papers_path = os.path.join(duc_dir, 'files')
        RankOnACL_GetModSysFiles(duc_dir, papers_path, pk_path, -1, 10)
    if test == "cedense":
        for ds in ["Dataset1", "Dataset2", "Dataset3", "Dataset4", "Dataset5"]:
            pk_path = os.path.join(cedense_dir, ds, 'pickle_CEnet')
            papers_path = os.path.join(cedense_dir, ds, 'files')
            RankOnKG_GetModSysFiles(os.path.join(cedense_dir, ds), papers_path, pk_path, 0)


if __name__ == '__main__':
    main()