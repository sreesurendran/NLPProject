import sys,os
import arff
import shutil
import xml.etree.ElementTree as ET

if len(sys.argv) < 4:
    print "USAGE: python generate_feature_vec.py <path_to_training_data> <path_to_test_files> <path_to_decision_tree_list> <feature_list>"
    sys.exit()

input_path = sys.argv[1].rstrip("/")
test_files_path = sys.argv[2].rstrip("/")
decision_tree_path = sys.argv[3].rstrip("/")
feature_list = sys.argv[4].split()

f_test_files = open(test_files_path,"r")
test_file_list = f_test_files.read().splitlines()
f_test_files.close()

f_decision_trees = open(decision_tree_path,"r")
decision_tree_list = f_decision_trees.read().splitlines()
f_decision_trees.close()

def get_cosine(a,b):
    if list(set(a)) != [0.0] and list(set(b)) != [0.0]:
        return round(numpy.inner(a, b)/(numpy.linalg.norm(a)*numpy.linalg.norm(b)), 3)
    else:
        return -1

#pull out the good contexts for this document
def getContexts(directory_path):
    candidates = []
    if os.path.isdir(directory_path):
        for subdir, dirs, files in os.walk(directory_path):
            for curr_file in files:
                name,ext = os.path.splitext(curr_file)
                if ext == ".list":
                    f_document_list = open(subdir + os.sep + curr_file,"r")
                    documents_list = f_document_list.read().splitlines()
                    f_document_list.close()
                    if len(filter(lambda x: x!=0, documents_list)) != 0:
                        candidates.append(subdir)
    return candidates

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

if "papers_published_best" in feature_list or "papers_published_next_best" in feature_list or "common_authors" in feature_list:
    authors = getAuthorDict()

for file in test_file_list:
    arff_data = []
    feature_vec = []
    directory_path = input_path + os.sep + file
    candidate_contexts = getContexts(directory_path)    
    for context in candidate_contexts:
        for document in decision_tree_list:
            for feature in feature_list:
                if feature == "common_authors":
                
                elif feature == "paper_year":

                elif feature == "papers_published_best":

                elif feature == "papers_published_next_best":

                elif feature == "abstract":
                rep_tfidf = getDocumentTfidf(document)
                context_tfdif = getContextTfidf(context)
    arff_data.append(feature)
