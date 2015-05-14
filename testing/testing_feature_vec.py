import sys,os,gzip,pickle
import arff
import shutil
import xml.etree.ElementTree as ET
import scipy, numpy

if len(sys.argv) < 6:
    print "USAGE: python generate_feature_vec.py <path_to_training_data> <path_to_test_files> <path_to_decision_tree_list> <path_to_year_dict> <feature_list> <version_number>"
    sys.exit()

input_path = sys.argv[1].rstrip("/")
test_files_path = sys.argv[2].rstrip("/")
decision_tree_path = sys.argv[3].rstrip("/")
paper_year_path = sys.argv[4].rstrip("/")
feature_list = sys.argv[5].split()
version_number = sys.argv[6]

f_test_files = open(test_files_path,"r")
test_file_list = f_test_files.read().splitlines()
f_test_files.close()

f_decision_trees = open(decision_tree_path,"r")
decision_tree_list = f_decision_trees.read().splitlines()
f_decision_trees.close()

#pull out the good contexts for this document
def getContexts(directory_path):
    candidates = []
    #get citation folder path for this document
    citation_folder_path = directory_path + os.sep + "cit"
    #check if this document has a citation folder
    if os.path.isdir(citation_folder_path):
        #walk the cit folder for this document
        for current_context_folder, list_of_context_folders, files_in_context_folder in os.walk(citation_folder_path):
            #get documents.list file path for the currect context folder
            documents_list_file_path = current_context_folder + os.sep + "documents.list"
            #check if this context folder has a documents list file
            if os.path.isfile(documents_list_file_path):
                #open the documents list file for the current context folder and pull out the list of documents
                f_document_list = open(documents_list_file_path,"r")
                documents_list = f_document_list.read().splitlines()
                f_document_list.close()
                #check if the list of documents has a non zero entry. if yes, add the current context folder to the list of candidate
                #contexts for this document
                #note: we're adding the entire path for the current context folder to the list of candidate contexts for this
                #document
                if len(filter(lambda x: int(x)!=0, documents_list)) != 0:
                    candidates.append(current_context_folder)
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

if "paper_year" in feature_list:
    f_paper_year = open(paper_year_path,"r")
    paperyears = pickle.load(f_paper_year)
    f_paper_year.close()

def get_cosine(path1,path2,feature):
    if os.path.isfile(path1):
        f_i = gzip.open(path1,"r")
        i_tfidf= pickle.load(f_i)
        f_i.close()
    
    if os.path.isfile(path2):
        f_j = gzip.open(path2,"r")
        j_tfidf= pickle.load(f_j)
        f_j.close()
    
    if os.path.isfile(path1) and os.path.isfile(path2):
        return get_cosine_helper(i_tfidf,j_tfidf,feature)
    else:
        return -1

def get_cosine_helper(a, b, c):
    if c == 'abstract':
        if list(set(a)) != [0.0] and list(set(b)) != [0.0]:
            return round (numpy.inner (a, b) / (numpy.linalg.norm (a) * numpy.linalg.norm (b)), 3)
    else:
        helper1 = (a * a.T).toarray ()[0][0]
        helper2 = (b * b.T).toarray ()[0][0]
        if helper1 != 0 and helper2 != 0:
            return round (((a * b.T).toarray()[0][0]) / ((helper1 * helper2)**0.5), 3)
    return -1        

for file in test_file_list:
    directory_path = input_path + os.sep + file
    candidate_contexts = getContexts(directory_path)        
    for context in candidate_contexts:
        #'context' has the entire path for the candidate context folder
        arff_data = []        
        for document in decision_tree_list:
            doc_int = int(document)
            feature_vec = []
            for feature in feature_list:                        
                if feature == "papers_published_best":
                    feature_vec.append(getAuthorPubCount(authors[0],authors[1],doc_int,1))

                elif feature == "papers_published_next_best":
                    feature_vec.append(getAuthorPubCount(authors[0],authors[1],doc_int,2))

                elif feature == "common_authors":
                    feature_vec.append(getNoOfCommonAuthors(authors[0],authors[1],int(file),doc_int))

                elif feature == "paper_year":
                    feature_vec.append(paperyears.get (doc_int, 0))

                elif feature == "abstract":
                    i_abstract_file_path = input_path + os.sep + file + os.sep + file + ".abstract.words.tfidf.gz"
                    j_abstract_file_path = input_path + os.sep + document + os.sep + document + ".abstract.words.tfidf.gz"
                    cosine = get_cosine(i_abstract_file_path,j_abstract_file_path,feature)    
                    feature_vec.append(cosine)

                else:
                    #all context aware features go here
                    context_tfidf_path = context + os.sep + context.split(os.sep)[-1] + "_" + curr_feature + ".words.tfidf.gz"
                    document_tfidf_path = input_path + os.sep + document + os.sep + document + ".rep." + feature + ".gz"
                    cosine = get_cosine(context_tfidf_path,document_tfidf_path,feature) 
                    feature_vec.append(cosine)                                

            documents_list_file_path = context + os.sep + "documents.list"
            if os.path.isfile(documents_list_file_path):
                f_documents_list = open(documents_list_file_path,"r")
                documents_cited = f_documents_list.read().splitlines()
                f_documents_list.close()
                if document in documents_cited:
                    feature_vec.append(arff.Nominal('yes'))
                else:
                    feature_vec.append(arff.Nominal('no'))   

            arff_data.append(feature_vec)         

        #write out the arff file
        headers = list(feature_list);
        headers.append('cited')
        feature_vec_file_path = context + os.sep + context.split(os.sep)[-1] + ".v" + version_number + ".arff"
        output = arff.Writer(feature_vec_file_path,relation='citation_data',names=headers)
        output.pytypes[arff.Nominal] = '{yes,no}'
        for value in arff_data:
            output.write(value)
        output.close()    


