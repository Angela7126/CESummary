# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
from Model_CEiter.MyModel3 import MyModel3
from Model_CEiter.MySecModel3 import MySecModel3
from Model_CEiter.MySecTitleNetwork3 import MySecTitleModel3
from Model_CEiter.sxpContextModel3 import conTextModel3
from Model_CEiter.sxpHybridGraph3 import HybridGraph3
from Model_CEiter.MySecContextModel3 import SecConTextModel3
from cmyToolkit import *
from cmyDoTestPyrouge import *
from os import system

# ------------ some dict object ---------------
idname = {'mymodel3': '01',  'context3': '05', 'mysecmodel3': '06', 'myseccontextmodel3': '07', 'hybrid3': '08', 'sectitle3': '09'}


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
def evaluate_all_kg(fp, papers_path, pk_path, modeltype='mymodel3', inc_abscon=True, useabstr=1, maxtxt=-1, fname_topk_dict={}, bias=0.8):
    # -- if modeltype is not in our model list, not execute the following process --
    if modeltype not in idname.keys():
        return
    print "model type =", modeltype
    # systemdir should be managed accoding to the inc_abscon parameter
    if not inc_abscon:
        system_dir = os.path.join(fp, 'systemIter_'+str(bias)+'_1')
        system_mandir = os.path.join(fp, 'systemIter_'+str(bias)+'_man1')
    else:
        system_dir = os.path.join(fp, 'systemIter_'+str(bias)+'_2')
        system_mandir = os.path.join(fp, 'systemIter_'+str(bias)+'_man2')
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
        if modeltype == 'mymodel3':
            old_model = MyModel3(pickle_path, opt='nonce')
            sysce_model = MyModel3(pickle_path, opt='sysce', bias=bias)
            if len(old_model.text.man_CE_list) > 0:
                mance_model = MyModel3(pickle_path, opt='mance', bias=bias)
            else:
                mance_model = None
        if modeltype == 'context3':
            old_model = conTextModel3(pickle_path, opt='nonce')
            sysce_model = conTextModel3(pickle_path, opt='sysce', bias=bias)
            if len(old_model.text.man_CE_list) > 0:
                mance_model = conTextModel3(pickle_path, opt='mance', bias=bias)
            else:
                mance_model = None
        if modeltype == 'mysecmodel3':
            old_model = MySecModel3(pickle_path, opt='nonce')
            sysce_model = MySecModel3(pickle_path, opt='sysce', bias=bias)
            if len(old_model.text.man_CE_list) > 0:
                mance_model = MySecModel3(pickle_path, opt='mance', bias=bias)
            else:
                mance_model = None
        if modeltype == 'myseccontextmodel3':
            old_model = SecConTextModel3(pickle_path, opt='nonce')
            sysce_model = SecConTextModel3(pickle_path, opt='sysce', bias=bias)
            if len(old_model.text.man_CE_list) > 0:
                mance_model = SecConTextModel3(pickle_path, opt='mance', bias=bias)
            else:
                mance_model = None
        if modeltype == 'hybrid3':
            old_model = HybridGraph3(pickle_path, opt='nonce')
            sysce_model = HybridGraph3(pickle_path, opt='sysce', bias=bias)
            if len(old_model.text.man_CE_list) > 0:
                mance_model = HybridGraph3(pickle_path, opt='mance', bias=bias)
            else:
                mance_model = None
        if modeltype == 'sectitle3':  # MySecTitleNetwork.py
            old_model = MySecTitleModel3(pickle_path, opt='nonce')
            sysce_model = MySecTitleModel3(pickle_path, opt='sysce', bias=bias)
            if len(old_model.text.man_CE_list) > 0:
                mance_model = MySecTitleModel3(pickle_path, opt='mance', bias=bias)
            else:
                mance_model = None

        # -- get the .html file's suffix NO. --
        if modeltype in idname.keys():
            idstr = idname[modeltype]
        # -- save original model ranked topk sentences to text --
        tops = old_model.OutPutTopKSent(topk, useabstr, maxtxt)
        st = ProduceSystem(tops, file_name, 1)
        topksent_path = os.path.join(system_dir, file_name + '.html.' + idstr)
        WriteStrFile(topksent_path, st, 'utf-8')
        if mance_model:
            topksent_path = os.path.join(system_mandir, file_name + '.html.' + idstr)
            WriteStrFile(topksent_path, st, 'utf-8')
        # -- save pattern matched cause-effect links ranked topk sentences to text --
        tops = sysce_model.OutPutTopKSent(topk, useabstr, maxtxt)
        st = ProduceSystem(tops, file_name, 1)
        topksent_path = os.path.join(system_dir, file_name + '.html.' + str(30 + int(idstr)))
        WriteStrFile(topksent_path, st, 'utf-8')
        # -- save manual labeled cause-effect links ranked topk sentences to text --
        if mance_model:
            tops = mance_model.OutPutTopKSent(topk, useabstr, maxtxt)
            st = ProduceSystem(tops, file_name, 1)
            topksent_path = os.path.join(system_mandir, file_name + '.html.' + str(20 + int(idstr)))
            WriteStrFile(topksent_path, st, 'utf-8')
    print "ranking complete"


def evaluate_all_acl(fp, papers_path, pk_path, modeltype='mymodel3', inc_abscon=True, useabstr=1, maxtxt=-1, topk=10, bias=0.8):
    # -- if modeltype is not in our model list, not execute the following process --
    if modeltype not in idname.keys():
        return
    print "model type =", modeltype
    # systemdir should be managed accoding to the inc_abscon parameter
    if not inc_abscon:
        system_dir = os.path.join(fp, 'systemIter_' + str(bias) + '_html1')
    else:
        system_dir = os.path.join(fp, 'systemIter_' + str(bias) + '_html2')
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)

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
        if modeltype == 'mymodel3':
            old_model = MyModel3(pickle_path, opt='nonce')
            sysce_model = MyModel3(pickle_path, opt='sysce', bias=bias)
        if modeltype == 'context3':
            old_model = conTextModel3(pickle_path, opt='nonce')
            sysce_model = conTextModel3(pickle_path, opt='sysce', bias=bias)
        if modeltype == 'mysecmodel3':
            old_model = MySecModel3(pickle_path, opt='nonce')
            sysce_model = MySecModel3(pickle_path, opt='sysce', bias=bias)
        if modeltype == 'myseccontextmodel3':
            old_model = SecConTextModel3(pickle_path, opt='nonce')
            sysce_model = SecConTextModel3(pickle_path, opt='sysce', bias=bias)
        if modeltype == 'hybrid3':
            old_model = HybridGraph3(pickle_path, opt='nonce')
            sysce_model = HybridGraph3(pickle_path, opt='sysce', bias=bias)
        if modeltype == 'sectitle3':  # MySecTitleNetwork.py
            old_model = MySecTitleModel3(pickle_path, opt='nonce')
            sysce_model = MySecTitleModel3(pickle_path, opt='sysce', bias=bias)

        # -- get the .html file's suffix NO. --
        if modeltype in idname.keys():
            idstr = idname[modeltype]
        # -- save original model ranked topk sentences to text --
        tops = old_model.OutPutTopKSent(topk, useabstr, maxtxt)
        st = ProduceSystem(tops, file_name, 1)
        topksent_path = os.path.join(system_dir, file_name + '.html.' + idstr)
        WriteStrFile(topksent_path, st, 'utf-8')
        # -- save pattern matched cause-effect links ranked topk sentences to text --
        tops = sysce_model.OutPutTopKSent(topk, useabstr, maxtxt)
        st = ProduceSystem(tops, file_name, 1)
        topksent_path = os.path.join(system_dir, file_name + '.html.' + str(30 + int(idstr)))
        WriteStrFile(topksent_path, st, 'utf-8')
    print "ranking complete"


def evaluate_all_duc(fp, papers_path, pk_path, modeltype='mymodel3', inc_abscon=True, useabstr=1, maxtxt=-1, topk=10, bias=0.8):
    # -- if modeltype is not in our model list, not execute the following process --
    if modeltype not in idname.keys():
        return
    print "model type =", modeltype
    # systemdir should be managed accoding to the inc_abscon parameter
    if not inc_abscon:
        system_dir = os.path.join(fp, 'systemIter_' + str(bias) + '_html1')
    else:
        system_dir = os.path.join(fp, 'systemIter_' + str(bias) + '_html2')
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)

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
        if modeltype == 'mymodel3':
            old_model = MyModel3(pickle_path, opt='nonce')
            sysce_model = MyModel3(pickle_path, opt='sysce', bias=bias)
        if modeltype == 'context3':
            old_model = conTextModel3(pickle_path, opt='nonce')
            sysce_model = conTextModel3(pickle_path, opt='sysce', bias=bias)
        if modeltype == 'mysecmodel3':
            old_model = MySecModel3(pickle_path, opt='nonce')
            sysce_model = MySecModel3(pickle_path, opt='sysce', bias=bias)
        if modeltype == 'myseccontextmodel3':
            old_model = SecConTextModel3(pickle_path, opt='nonce')
            sysce_model = SecConTextModel3(pickle_path, opt='sysce', bias=bias)
        if modeltype == 'hybrid3':
            old_model = HybridGraph3(pickle_path, opt='nonce')
            sysce_model = HybridGraph3(pickle_path, opt='sysce', bias=bias)
        if modeltype == 'sectitle3':  # MySecTitleNetwork.py
            old_model = MySecTitleModel3(pickle_path, opt='nonce')
            sysce_model = MySecTitleModel3(pickle_path, opt='sysce', bias=bias)

        # -- get the .html file's suffix NO. --
        if modeltype in idname.keys():
            idstr = idname[modeltype]
        # -- save original model ranked topk sentences to text --
        tops = old_model.OutPutTopKSent(topk, useabstr, maxtxt)
        st = ProduceSystem(tops, file_name, 1)
        topksent_path = os.path.join(system_dir, file_name + '.html.' + idstr)
        WriteStrFile(topksent_path, st, 'utf-8')
        # -- save pattern matched cause-effect links ranked topk sentences to text --
        tops = sysce_model.OutPutTopKSent(topk, useabstr, maxtxt)
        st = ProduceSystem(tops, file_name, 1)
        topksent_path = os.path.join(system_dir, file_name + '.html.' + str(30 + int(idstr)))
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
    # ---- in_abscon determines whether abstraction and conclusion sentence in ranking process ----
    for bias in range(10, 21):
        bias /= 20.0
        print "current bias = ", bias
        for inc_abscon in [True, False]:
            evaluate_all_kg(path, papers_path, pk_path, 'mymodel3', inc_abscon, useabscon, maxwords,  fname_topk_dict, bias=bias)
            evaluate_all_kg(path, papers_path, pk_path, 'context3', inc_abscon, useabscon, maxwords,  fname_topk_dict, bias=bias)
            evaluate_all_kg(path, papers_path, pk_path, 'mysecmodel3', inc_abscon, useabscon, maxwords,  fname_topk_dict, bias=bias)
            evaluate_all_kg(path, papers_path, pk_path, 'myseccontextmodel3', inc_abscon, useabscon, maxwords,  fname_topk_dict, bias=bias)
            evaluate_all_kg(path, papers_path, pk_path, 'hybrid3', inc_abscon, useabscon, maxwords,  fname_topk_dict, bias=bias)
            evaluate_all_kg(path, papers_path, pk_path, 'sectitle3', inc_abscon, useabscon, maxwords,  fname_topk_dict, bias=bias)
    for bias in range(10, 21):
        bias /= 20.0
        model_path = os.path.join(path, 'model_html')
        system_dir = ['systemIter_'+str(bias)+'_man1', 'systemIter_'+str(bias)+'_man2', 'systemIter_'+str(bias)+'_1', 'systemIter_'+str(bias)+'_2']
        system_idlst = [['01', '21', '05', '25', '06', '26', '07', '27', '08', '28', '09', '29'],
                        ['01', '31', '05', '35', '06', '36', '07', '37', '08', '38', '09', '39']]
        TestCallKG(path, model_path, system_dir, system_idlst)

    return


def RankOnACL_GetModSysFiles(path, papers_path, pk_path, maxwords=0, topksents=10):
    # ---- Prepare comparing text ----
    # for abscon in [1,2]:
    #     GetComparingText(path, papers_path, pk_path, abscon)
    useabscon = 1
    # ---- in_abscon determines whether abstraction and conclusion sentence in ranking process ----
    for bias in range(10, 21):
        bias /= 20.0
        print "current bias = ", bias
        for inc_abscon in [True, False]:
            evaluate_all_acl(path, papers_path, pk_path, 'mymodel3', inc_abscon, useabscon, maxwords,  topk=topksents, bias=bias)
            evaluate_all_acl(path, papers_path, pk_path, 'context3', inc_abscon, useabscon, maxwords, topk=topksents, bias=bias)
            evaluate_all_acl(path, papers_path, pk_path, 'mysecmodel3', inc_abscon, useabscon, maxwords, topk=topksents, bias=bias)
            evaluate_all_acl(path, papers_path, pk_path, 'myseccontextmodel3', inc_abscon, useabscon, maxwords, topk=topksents, bias=bias)
            evaluate_all_acl(path, papers_path, pk_path, 'hybrid3', inc_abscon, useabscon, maxwords, topk=topksents, bias=bias)
            evaluate_all_acl(path, papers_path, pk_path, 'sectitle3', inc_abscon, useabscon, maxwords, topk=topksents, bias=bias)
    for bias in range(10, 21):
        bias /= 20.0
        model_path = os.path.join(acl_dir, 'model_html')
        system_dir = ['systemIter_' + str(bias) + '_html1', 'systemIter_' + str(bias) + '_html2']
        system_idlst = [['01', '31', '05', '35', '06', '36', '07', '37', '08', '38', '09', '39']]
        TestCallACL(model_path, system_dir, system_idlst)
    return


def RankOnDUC_GetModSysFiles(path, papers_path, pk_path, maxwords=0, topksents=10):
    # ---- Prepare comparing text ----
    # for abscon in [1,2]:
    #     GetComparingText(path, papers_path, pk_path, abscon)
    useabscon = 1
    # ---- in_abscon determines whether abstraction and conclusion sentence in ranking process ----
    for bias in range(1, 21):
        bias /= 20.0
        print "current bias = ", bias
        for inc_abscon in [True, False]:
            evaluate_all_duc(path, papers_path, pk_path, 'mymodel3', inc_abscon, useabscon, maxwords,  topk=topksents, bias=bias)
            evaluate_all_duc(path, papers_path, pk_path, 'context3', inc_abscon, useabscon, maxwords, topk=topksents, bias=bias)
            evaluate_all_duc(path, papers_path, pk_path, 'mysecmodel3', inc_abscon, useabscon, maxwords, topk=topksents, bias=bias)
            evaluate_all_duc(path, papers_path, pk_path, 'myseccontextmodel3', inc_abscon, useabscon, maxwords, topk=topksents, bias=bias)
            evaluate_all_duc(path, papers_path, pk_path, 'hybrid3', inc_abscon, useabscon, maxwords, topk=topksents, bias=bias)
            evaluate_all_duc(path, papers_path, pk_path, 'sectitle3', inc_abscon, useabscon, maxwords, topk=topksents, bias=bias)
    for bias in range(10, 21):
        bias /= 20.0
        model_path = os.path.join(duc_dir, 'model_html')
        system_dir = ['systemIter_' + str(bias) + '_html1', 'systemIter_' + str(bias) + '_html2']
        system_idlst = [['01', '31', '05', '35', '06', '36', '07', '37', '08', '38', '09', '39']]
        TestCallDUC(model_path, system_dir, system_idlst)
    return


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
        RankOnACL_GetModSysFiles(acl_dir, papers_path, pk_path, 0)
    if test == 'duc':
        pk_path = os.path.join(duc_dir, 'pickle_CEnet1')
        papers_path = os.path.join(duc_dir, 'files')
        RankOnDUC_GetModSysFiles(duc_dir, papers_path, pk_path, 0)
    if test == "cedense":
        for ds in ["Dataset1", "Dataset2", "Dataset3", "Dataset4", "Dataset5"]:
            pk_path = os.path.join(cedense_dir, ds, 'pickle_CEnet')
            papers_path = os.path.join(cedense_dir, ds, 'files')
            RankOnKG_GetModSysFiles(os.path.join(cedense_dir, ds), papers_path, pk_path, 0)

if __name__ == '__main__':
    main()


