import sys, os
import pickle
from collections import OrderedDict
import arff
import string, shutil
import xml.etree.ElementTree as ET
import gzip

if(len(sys.argv) < 7):
    print("USAGE: python generate_feature_vec.py <input_path> <feature> <path_to_year_dict> <path_to_titles> <decision_tree_list> <version_number>")
    sys.exit()

input_path = sys.argv[1].rstrip("/")
feature_list = sys.argv[2].split()
print "Feature List: ", feature_list
paper_year_path = sys.argv[3].rstrip("/")
titles_path = sys.argv[4]
decision_tree_path = sys.argv[5]
tree_version_number = sys.argv[6]
features_dict = {}

f_decision_trees = open(decision_tree_path,"r")
decision_tree_list = f_decision_trees.read().splitlines()
f_decision_trees.close()

def getAuthorDict():
    tFile = open (titles_path, 'r')
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
    listOfPubPapers = map (lambda x: len (authDict.get(x,[])), fileToAuthDict.get(subdir,[]))
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
    return len (set (fileToAuthDict.get (paper1, [])) & set (fileToAuthDict.get (paper2, [])))

totCount = 0

if "paper_year" in feature_list:
    f_paper_year = open(paper_year_path,"r")
    paperyears = pickle.load(f_paper_year)
    f_paper_year.close()
    #paperyears = createPaperYearDict()
    #print paperyears

if "papers_published_best" in feature_list or "papers_published_next_best" in feature_list or "common_authors" in feature_list:
    authors = getAuthorDict()

for subdir, dirs, files in os.walk(input_path):
    #print "SUBDIR: " + subdir
    if totCount % 4000 == 0:
        print totCount
    totCount += 1

    if subdir == input_path:
        continue
    subdir_basename = os.path.basename(subdir)
    if subdir_basename not in decision_tree_list:
        continue
    inlink_lst = []
    j_list = []
    j_path_list = []
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
                    if inner_subdir == search_document_path:
                        continue
                    try:
                        j_list.append(int(search_document))
                    except:
                        pass
                    j_path_list.append(inner_subdir)

    #print "J_LIST: "
    #print j_list

    for feature in feature_list:
        feature_file_dict = []
        feature_file_path = subdir + os.sep + subdir_basename + "." + feature + ".feature.gz"
        if os.path.isfile(feature_file_path):
            f_feature = gzip.open(feature_file_path,"r")
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
                common_authors_list.append(getNoOfCommonAuthors(authors[0],authors[1],int(subdir_basename),value))
            feature_dict[feature] = common_authors_list

        if feature == "paper_year":
            paper_year_list = []
            for value in j_list:
                paper_year_list.append(paperyears.get (value, 0))
            feature_dict[feature] = paper_year_list

        if feature == "abstract":
            abstract_file_path = subdir + os.sep + subdir_basename + ".abstractcosine.gz"
            if os.path.isfile(abstract_file_path):
                f_abstract = gzip.open(abstract_file_path,"r")
                abstract_file_dict = pickle.load(f_abstract)
                f_abstract.close()
                abstract_list = []
                for value in j_list:
                    abstract_list.append(abstract_file_dict[str(value)])
                feature_dict[feature] = abstract_list

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
        #print "MASTER_LIST: " 
        #print master_list
        for x in xrange(0,len(master_list)):
            new_value = master_list[x]
            documents_list_file_path = j_path_list[x] + os.sep + "documents.list"
            if os.path.isfile(documents_list_file_path):
                f_documents_list = open(documents_list_file_path)
                documents_cited = f_documents_list.read().splitlines()
                f_documents_list.close()
                if subdir_basename in documents_cited:
                    new_value.append(arff.Nominal('yes'))
                else:
                    new_value.append(arff.Nominal('no'))
            master_list[x] = new_value
        feature_vec_file_path = subdir + os.sep + subdir_basename + ".arff" + tree_version_number

        headers = list(feature_list);
        headers.append('cited')
        #print "HEADERS:"
        #print headers
        output = arff.Writer(feature_vec_file_path,relation='citation_data',names=headers)
        output.pytypes[arff.Nominal] = '{yes,no}'
        for value in master_list:
            output.write(value)
        output.close()
