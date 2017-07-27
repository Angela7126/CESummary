# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
from pyrouge import MyRouge155
from cmyToolkit import *
import xlsxwriter
import os
import re

# ------------ set global dict object model_name ---------------
model_name = {'00': 'CEPure_MCE', '01': 'Para', '02': 'TFIDF', '03': 'GS', '04': 'GW', '05': 'Context',
              '06': 'Section', '07': 'Sec_Context', '08': 'GS_Context', '09': 'SecTitle', '10':'CEPure_RCE',
              '21': 'Para_MCE', '22': 'TFIDF_MCE', '23': 'GS_MCE', '24': 'GW_MCE', '25': 'Context_MCE',
              '26': 'Section_MCE', '27': 'SecContext_MCE', '28': 'GS_Context_MCE', '29': 'SecTitle_MCE',
              '31': 'Para_RCE', '32': 'TFIDF_RCE', '33': 'GS_RCE', '34': 'GW_RCE', '35': 'Context_RCE',
              '36': 'Section_RCE', '37': 'SecContext_RCE', '38': 'GS_Context_RCE', '39': 'SecTitle_RCE',
              '41': 'Para_CEBias', '42': 'TFIDF_CEBias', '43': 'GS_CEBias', '44': 'GW_CEBias', '45': 'Context_CEBias',
              '46': 'Section_CEBias', '47': 'Sec_Context_CEBias', '48': 'GS_Context_CEBias', '49': 'SecTitle_CEBias',
              '51': 'Para_CEIter', '55': 'Context_CEIter', '56': 'Section_CEIter', '57': 'Sec_Context_CEIter',
              '58': 'GS_Context_CEIter', '59': 'SecTitle_CEBias'
              }

def sub_dict(somedict, somekeys, default=None):
    return dict([(k, somedict.get(k, default)) for k in somekeys])

#######################################################################################
# ------------------------------- Plot the Rouge result ----------------------------- #
#######################################################################################
def TestParseMultiSysOutputKG(system_path, system_idstr):
    fname = os.path.join(system_path, 'KG_'+ '_'.join(system_idstr)+'.pk.txt')
    system_id_set = {}
    for idstr in system_idstr:
        system_id_set[idstr] = {}
    system_id_set_result = ParseMultiSysOutput(fname, system_id_set)
    pkname = fname+'.pk'
    StoreSxptext(system_id_set_result, pkname)
    ProcessRougeScore('kg_', pkname, system_idstr, system_path)

def TestParseMultiSysOutputKGSec(system_path, system_idstr, fhead):
    fname = os.path.join(system_path, fhead + '_'.join(system_idstr) + '.pk.txt')
    system_id_set = {}
    for idstr in system_idstr:
        system_id_set[idstr] = {}
    system_id_set_result = ParseMultiSysOutput(fname, system_id_set)
    pkname = fname+'.pk'
    StoreSxptext(system_id_set_result, pkname)
    ProcessRougeScore(fhead, pkname, system_idstr, system_path)

def TestParseMultiSysOutputACL(system_path, system_idstr):
    fname = os.path.join(system_path, 'ACL_'+'_'.join(system_idstr)+'.pk.txt')
    system_id_set = {}
    for idstr in system_idstr:
        system_id_set[idstr] = {}
    system_id_set_result = ParseMultiSysOutput(fname, system_id_set)
    pkname = fname+'.pk'
    StoreSxptext(system_id_set_result, pkname)
    ProcessRougeScore('acl_', pkname, system_idstr, system_path)

def TestParseMultiSysOutputDUC(system_path, system_idstr):
    fname = os.path.join(system_path, 'DUC_'+'_'.join(system_idstr)+'.pk.txt')
    system_id_set = {}
    for idstr in system_idstr:
        system_id_set[idstr] = {}
    system_id_set_result = ParseMultiSysOutput(fname, system_id_set)
    pkname = fname+'.pk'
    StoreSxptext(system_id_set_result, pkname)
    ProcessRougeScore('duc_', pkname, system_idstr, system_path)

def ParseMultiSysOutput(fname, system_id_set):
    txt = ReadTextUTF(fname)
    recall_pattern = re.compile(r'(\d\d) (ROUGE-\S+) (Average_\w):\s+(\d.\d+)\s+' + r"\(95%-conf.int. (\d.\d+) - (\d.\d+)\)")
    for line in txt.split("\n"):
        print line
        match = recall_pattern.match(line)
        if match:
            sys_id, rouge_type, metric, result, conf_begin, conf_end = \
                match.groups()
            print sys_id,rouge_type, metric, result, conf_begin, conf_end
            if rouge_type in system_id_set[sys_id]:
                a = system_id_set[sys_id][rouge_type]
                if a is None:
                    a = []
            else:
                a = []
            a.append([metric,result, conf_begin, conf_end])
            system_id_set[sys_id][rouge_type] = a
    return system_id_set


def ProcessRougeScore(fhead, pkname, system_idstr, system_path):
    ds = LoadSxptext(pkname)
    print ds
    modelname = sub_dict(model_name, system_idstr)
    metric_set = [
        ['ROUGE-1', 'Average_P', 'Average_R', 'Average_F'],
        ['ROUGE-2', 'Average_P', 'Average_R', 'Average_F'],
        ['ROUGE-3', 'Average_P', 'Average_R', 'Average_F'],
        ['ROUGE-4', 'Average_P', 'Average_R', 'Average_F'],
        ['ROUGE-L', 'Average_P', 'Average_R', 'Average_F']
    ]
    nsection = 1
    nrow = nsection + 1
    nc = 1
    coorname = ['precision', 'recall', 'f-score']
    colorset = ['r', 'b', 'g', 'c', 'm', 'y', 'k']
    fname = os.path.join(system_path, fhead + 'rouge_score_'+system_path.split('\\')[-1]+'_'+'_'.join(system_idstr)+'.xlsx')
    print fname
    workbook = xlsxwriter.Workbook(fname)
    worksheet = workbook.add_worksheet()
    for em in metric_set:  # weplot one bar figure
        title = em[0]
        print title

        value = str(title)
        rown = nsection
        coln = 0
        for ic in range(len(em)):
            value = str(em[ic])
            worksheet.write(rown, coln + ic, value)
        dataset = []
        metric_name = em[1:]

        for eachmodel in system_idstr:  # we extract each model's metric
            legendname = modelname[eachmodel]  # get each model's name
            value = str(legendname)  # get each model's name
            rown = rown + 1
            coln = 0
            print '1write', rown, coln, value
            worksheet.write(rown, coln, value)

            datarow = []
            for eachm in metric_name:
                rown = rown
                coln += 1
                result_set = ds[eachmodel][title]
                for each_m in result_set:
                    if each_m[0] == eachm:
                        value = str(each_m[1])  # avergage score, not confidence value)
                        print '2write', rown, coln, value
                        worksheet.write(rown, coln, value)
                        datarow.append(float(value))
            dataset.append([legendname, datarow])

        nsection = rown + 2
        print dataset
        # PlotBarFromCoordSet(title, dataset, coorname, colorset)
        # plt.savefig(os.path.join(system_path, fhead + title + '.jpg'))
    workbook.close()

#######################################################################################
# --------------------- Evaluate the ranked sentence use rouge  --------------------- #
#######################################################################################
def TestKG(system_idstr, model_path, system_path):
    modelpattern = r'f#ID#.txt.[A-Z].html'
    systempattern = r'^f(\d+).txt.html'

    system_name = 'KG_'+ '_'.join(system_idstr)+'.pk'
    output_fname = system_name  # "output_set_model1_inc.pk"
    CallMyPyrouge(system_path, model_path, modelpattern, systempattern, output_fname, system_idstr)

def TestKGSec(system_idstr, model_path, system_path, modelpattern, systempattern, fhead):
    system_name = fhead + '_'.join(system_idstr) + '.pk'
    output_fname = system_name  # "output_set_model1_inc.pk"
    CallMyPyrougeSec(system_path, model_path, modelpattern, systempattern, output_fname, system_idstr, fhead)

def TestACL(system_idstr, model_path, system_path):
    modelpattern = r'P14-#ID#.xhtml.[A-Z].html'
    systempattern = r'^P14-(\d+).xhtml.html'

    system_name = 'ACL_'+'_'.join(system_idstr)+'.pk'
    output_fname = system_name  # "output_set_model1_inc.pk"
    CallMyPyrouge(system_path, model_path, modelpattern, systempattern, output_fname, system_idstr)

def TestDUC(system_idstr, model_path, system_path):
    modelpattern = r'D\d\d\d.P.100.[A-Z].[A-Z].#ID#.html'
    systempattern = r'^(\w+-\w+).html'

    system_name = 'DUC_'+'_'.join(system_idstr)+'.pk'
    output_fname = system_name  # "output_set_model1_inc.pk"
    CallMyPyrouge(system_path, model_path, modelpattern, systempattern, output_fname, system_idstr)

def CallMyPyrouge(system_path, model_path, modelpattern, systempattern, output_fname, system_idstr):
    perlpathname = r'D:\Program Files\Perl\bin\perl'
    conf_path = os.path.join(system_path, 'rouge_conf_' + '_'.join(system_idstr) + '.xml')
    print system_path, systempattern, modelpattern
    output_set = []
    output = RunPaperMyRougeHtml(system_path, model_path, modelpattern, systempattern, conf_path, perlpath=perlpathname, system_idstr=system_idstr)
    output_set.append(output)
    output_fname = os.path.join(system_path, output_fname)
    StoreSxptext(output_set, output_fname)
    WriteStrFile(output_fname +'.txt', output, 'utf-8')

def CallMyPyrougeSec(system_path, model_path, modelpattern, systempattern, output_fname, system_idstr, fhead):
    perlpathname = r'D:\Program Files\Perl\bin\perl'
    conf_path = os.path.join(system_path, fhead + 'rouge_conf_' + '_'.join(system_idstr) + '.xml')
    print system_path, systempattern, modelpattern
    output_set = []
    output = RunPaperMyRougeHtml(system_path, model_path, modelpattern, systempattern, conf_path, perlpath=perlpathname, system_idstr=system_idstr)
    output_set.append(output)
    output_fname = os.path.join(system_path, output_fname)
    StoreSxptext(output_set, output_fname)
    WriteStrFile(output_fname +'.txt', output, 'utf-8')

def RunPaperMyRougeHtml(system_path, model_path, modelpattern, systempattern, config_file_path=None, perlpath=r'D:\Program Files\Perl\bin\perl', system_idstr=['None']):
    r = MyRouge155()
    r.system_dir = system_path
    r.config_file = config_file_path
    r.model_dir = model_path
    r.system_filename_pattern = systempattern
    r.model_filename_pattern = modelpattern
    output = r.evaluate(system_id=system_idstr, conf_path=config_file_path, PerlPath=perlpath)
    print(output)
    output_dict = r.output_to_dict(output)
    return output


#######################################################################################
# --------------------------------- Test functions  --------------------------------- #
#######################################################################################
def TestCallKG(path, model_path, system_dir, system_idlst):
    for idx, sysdir in enumerate(system_dir):
        system_path = os.path.join(path, sysdir)
        system_idstr = system_idlst[idx/2]
        TestKG(system_idstr, model_path, system_path)
        TestParseMultiSysOutputKG(system_path, system_idstr)

def TestCallACL(model_path, system_dir, system_idlst):
    for idx, sysdir in enumerate(system_dir):
        system_path = os.path.join(acl_dir, sysdir)
        system_idstr = system_idlst[idx/2]
        TestACL(system_idstr, model_path, system_path)
        TestParseMultiSysOutputACL(system_path, system_idstr)

def TestCallDUC(model_path, system_dir, system_idlst):
    for idx, sysdir in enumerate(system_dir):
        system_path = os.path.join(duc_dir, sysdir)
        system_idstr = system_idlst[idx / 2]
        TestDUC(system_idstr, model_path, system_path)
        TestParseMultiSysOutputDUC(system_path, system_idstr)

def TestCallKGSec(model_path, system_dir, system_idlst, modelpattern, systempattern, fhead):
    for system_path in system_dir:
        for system_idstr in system_idlst:
            TestKGSec(system_idstr, model_path, system_path, modelpattern, systempattern, fhead)
            TestParseMultiSysOutputKGSec(system_path, system_idstr, fhead)

#######################################################################################
# -------------------------------- Test Test functions  ------------------------------ #
#######################################################################################
def TestTestCallKG():
    model_path = os.path.join(kg_dir, 'model_html')
    system_dir = ['systemFliter_man1', 'systemFliter_man2', 'systemFliter_1', 'systemFliter_2']
    system_idlst = [
        ['01', '21', '02', '22', '03', '23', '04', '24', '05', '25', '06', '26', '07', '27', '08', '28', '09', '29'],
        ['01', '31', '02', '32', '03', '33', '04', '34', '05', '35', '06', '36', '07', '37', '08', '38', '09', '39']]
    TestCallKG(kg_dir, model_path, system_dir, system_idlst)

def TestTestCallACL():
    model_path = os.path.join(acl_dir, 'model_html')
    system_dir = ['system_html1', 'system_html2']
    system_idlst = [['01', '31', '02', '32', '03', '33', '04', '34', '05', '35', '06', '36', '07', '37', '08',
                    '38', '09', '39']]
    TestCallACL(model_path, system_dir, system_idlst)


def TestTestCallDUC():
    model_path = os.path.join(duc_dir, 'model_html')
    system_dir = ['system_html1', 'system_html2']
    system_idlst = [['01', '31', '02', '32', '03', '33', '04', '34', '05', '35', '06', '36', '07', '37', '08',
                     '38', '09', '39']]
    TestCallDUC(model_path, system_dir, system_idlst)

#######################################################################################
# --------------------------------- Main function ----------------------------------- #
#######################################################################################
def main():
    test = "kg"
    if test == "kg":
        TestTestCallKG()
    if test == "acl":
        TestTestCallACL()
    if test == "duc":
        TestTestCallDUC()

if __name__ == '__main__':
    main()