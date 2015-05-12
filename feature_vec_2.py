import sys, os
import pickle
from collections import OrderedDict
import arff
import string, shutil
import xml.etree.ElementTree as ET

if(len(sys.argv) < 4):
    print("USAGE: python generate_feature_vec.py <input_path> <feature> <path_to_year_dict>")
    sys.exit()

input_path = sys.argv[1].rstrip("/")
feature_list = sys.argv[2].split()
paper_year_path = sys.argv[3].rstrip("/")
features_dict = {}

def getAuthorDict():
    tFile = open ('/Users/sree/Desktop/Data/New/titles.out', 'r')
    # tFile = open (titleFile, 'r')
    authDict = dict()
    fileToAuthDict = dict()
    for line in tFile:
        helper = line.split ('||')
        if len(helper) > 1:
            i = 2
            docNumber = int(helper[1])
            authList = []
            while i < len(helper):
                temp = helper[i].split('|')
                fn = ''
                ln = ''
                if len(temp) == 1:
                    ln = temp[0].strip()
                elif len(temp) == 2:
                    ln = temp[0].strip()
                    fn = temp[1].strip()
                if fn != '':
                    fn = fn[0]
                key = ln + '|' + fn
                authList.append (key)
                helper2 = authDict.get(key, [])
                authDict[key] = helper2 + [docNumber]
                i += 1
            fileToAuthDict[docNumber] = authList
    tFile.close()
    return (authDict, fileToAuthDict)

def getAuthorPubCount (authDict, fileToAuthDict, subdir, mode):
    listOfPubPapers = map (lambda x: len (authDict[x]), fileToAuthDict[subdir])
    listOfPubPapers.sort()
    if len (listOfPubPapers) == 0:
        return 0
    if mode == 1:
        return listOfPubPapers[-1]
    if mode == 2 and len (listOfPubPapers) == 1:
        return listOfPubPapers[-1]
    return listOfPubPapers[-2]

def createPaperYearDict (directory):
    paperYearDict = dict ()
    for subdir in os.listdir (directory):
        if not subdir.isdigit():
            continue
        i = int (subdir)
        xmlTree = ET.parse (directory + subdir + '/' + subdir + '.xml')
        root = xmlTree.getroot ()
        dateNode = root.find('./fm/history/pub/date')
        if dateNode == None or dateNode[2] == None or dateNode[2].text == '':
            paperYearDict[i] = 0
        else:
            paperYearDict[i] = int(dateNode[2].text)
    return paperYearDict

def getNoOfCommonAuthors (authDict, fileToAuthDict, paper1, paper2):
    return len (set (fileToAuthDict[paper1]) & set (fileToAuthDict[paper2]))

for subdir, dirs, files in os.walk(input_path):
    if subdir == input_path:
        continue
    subdir_basename = os.path.basename(subdir)
    inlink_lst = []
    j_list = []
    feature_dict = OrderedDict()

    inlink_file_path = subdir + os.sep + subdir_basename + ".ref.inlink"
    if os.path.isfile(inlink_file_path):
        f_inlink = open(inlink_file_path,"r")
        inlink_list = f_inlink.read().splitlines()
        f_inlink.close()
        for search_document in inlink_list:
            search_document_path = input_path + os.sep + search_document + os.sep + "cit"
            if os.path.isdir(search_document_path):
                for inner_subdir, inner_dirs, inner_files in os.walk(search_document_path):
                    j_list.append(search_document)

    if "paper_year" in feature_list:
        f_paper_year = open(paper_year_path,"r")
        paperyears = pickle.load(f_paper_year)
        f_paper_year.close()
        #paperyears = createPaperYearDict()

    if "papers_published_best" in feature_list or "papers_published_next_best" in feature_list or "common_authors" in feature_list:
        authors = getAuthorDict()

    for feature in feature_list:
        feature_file_dict = []
        feature_file_path = subdir + os.sep + subdir_basename + "." + feature + ".feature"
        if os.path.isfile(feature_file_path):
            f_feature = open(feature_file_path,"r")
            feature_file_dict = pickle.load(f_feature)
            feature_dict[feature] = feature_file_dict.itervalues()
            f_feature.close()
        
        if feature == "papers_published_best":
            papers_published_best_list = []
            for value in j_list:
                papers_published_best_list.append(getAuthorPubCount(authors[0],authors[1],value,1))
            feature_dict[feature] = papers_published_best_list

        if feature == "papers_published_next_best":
            papers_published_next_best_list = []
            for value in j_list:
                papers_published_next_best_list.append(getAuthorPubCount(authors[0],authors[1],value,2))
            feature_dict[feature] = papers_published_next_best_list

        if feature == "common_authors":
            common_authors_list = []
            for value in j_list:
                common_authors_list.append(getNoOfCommonAuthors(authors[0],authors[1],subdir_basename,value))
            feature_dict[feature] = common_authors_list

        if feature == "paper_year":
            paper_year_list = []
            for value in j_list:
                paper_year_list.append(paperyears[value])
            feature_dict[feature] = paper_year_list

    list_of_feature_lists = []
    master_list = []
    for value in feature_dict.itervalues():
        list_of_feature_lists.append(value)

    for x in xrange(0,len(j_list)):
        row_list = []
        for feat in list_of_feature_lists:
            row_list.append(feat[x])
        master_list.append(row_list)

    if len(master_list) > 0 :
        print master_list
        for x in xrange(0,len(master_list)):
            new_value = master_list[x]
            documents_list_file_path = j_list[x] + os.sep + "documents.list"
            if os.path.isfile(documents_list_file_path):
                f_documents_list = open(documents_list_file_path)
                documents_cited = f_documents_list.read().splitlines()
                f_documents_list.close()
                if subdir_basename in documents_cited:
                    new_value.append(arff.Nominal('yes'))
                else:
                    new_value.append(arff.Nominal('no'))
            master_list[x] = new_value
        feature_vec_file_path = subdir + os.sep + subdir_basename + ".arff"

        headers = list(feature_list_arg);
        headers.append('cited')
        print headers
        output = arff.Writer(feature_vec_file_path,relation='citation_data',names=headers)
        output.pytypes[arff.Nominal] = '{yes,no}'
        for value in master_list:
            output.write(value)
        output.close()
