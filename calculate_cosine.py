import os,sys
import numpy, scipy
from collections import OrderedDict
import pickle
import gzip

if(len(sys.argv) < 5):
    print("USAGE: python calculate_cosine.py <input_path> <feature> <decision_tree_path> <restricted_set>")
    sys.exit()

input_path = sys.argv[1].rstrip("/")
feature = sys.argv[2]
decision_tree_path = sys.argv[3]
restricted_set_path = sys.argv[4]

f_decision_tree = open(decision_tree_path,"r")
decision_tree_list = f_decision_tree.read().splitlines()
f_decision_tree.close()

f_restricted_set = open(restricted_set_path,"r")
restricted_set = pickle.load (f_restricted_set)
f_restricted_set.close()

def get_cosine(a, b, c):
    if c == 'abstract':
        if list(set(a)) != [0.0] and list(set(b)) != [0.0]:
            return round (numpy.inner (a, b) / (numpy.linalg.norm (a) * numpy.linalg.norm (b)), 3)
    else:
        helper1 = (a * a.T).toarray ()[0][0]
        helper2 = (b * b.T).toarray ()[0][0]
        if helper1 != 0 and helper2 != 0:
            return round (((a * b.T).toarray()[0][0]) / ((helper1 * helper2)**0.5), 3)
    return -1

totCount = 0

#create the individual feature vector file
for subdir,dirs,files in os.walk(input_path):
    #print("SUBDIR: %s" % subdir)
    if totCount % 4000 == 0:
        print totCount
    totCount += 1
    if subdir == input_path:
        continue
    subdir_basename = os.path.basename(subdir)

    if subdir_basename not in decision_tree_list:
        continue

    check_path_exists = subdir + os.sep + subdir_basename + "." + feature + ".feature.gz"

    # if os.path.isfile(check_path_exists):
    #     continue

    if feature == "abstract":
        rep_file_path = subdir + os.sep + subdir_basename + ".abstract.words.tfidf.gz"
    else:
        rep_file_path = subdir + os.sep + subdir_basename + ".rep." + feature + ".gz"
    
    #print "REP FILE PATH: " + rep_file_path
    if os.path.isfile(rep_file_path):
        f_rep = gzip.open(rep_file_path,"r")
        rep_tfidf = pickle.load(f_rep)
        f_rep.close()
        feature_vec = OrderedDict()
        abstract_dict = OrderedDict()
    else:
        continue

    inlink_file_path = subdir + os.sep + subdir_basename + ".ref.inlink"
    if os.path.isfile(inlink_file_path):
        f_inlinks_candidates = open(inlink_file_path,"r")
        search_list = f_inlinks_candidates.read().splitlines()
        f_inlinks_candidates.close()
        for search_document in search_list:
            if feature == "abstract":
                abstract_tfidf_path = input_path + os.sep + search_document + os.sep + search_document + ".abstract.words.tfidf.gz"
                #print "ABSTRACT PATH: " + abstract_tfidf_path
                if os.path.isfile(abstract_tfidf_path):
                    f_abstract = gzip.open(abstract_tfidf_path,"r")
                    abstract_tfidf = pickle.load(f_abstract)
                    f_abstract.close()
                    abstract_cosine = get_cosine(rep_tfidf,abstract_tfidf, feature)
                    abstract_dict[search_document] = abstract_cosine
            
            c_list = restricted_set.get(int(search_document),[])

            search_document_path = input_path + os.sep + search_document + os.sep + "cit"
            if os.path.isdir(search_document_path):
                for c in c_list:
                    context_folder_path = search_document_path + os.sep + c
                    if os.path.isdir(context_folder_path):
                        tfidf_file_path = context_folder_path + os.sep + c + "_" + feature + ".words.tfidf.gz"
                        if os.path.isfile(tfidf_file_path):
                            f_arg = gzip.open(tfidf_file_path,"r")
                            arg_tfidf = pickle.load(f_arg)
                            f_arg.close()
                            cosine = get_cosine(rep_tfidf,arg_tfidf, feature)
                            feature_vec[context_folder_path] = cosine


    if feature != "abstract":
        feature_vec_file_path = subdir + os.sep + subdir_basename + "." + feature + ".feature.gz"
        f_feature = gzip.open(feature_vec_file_path,"w")
        pickled_list = pickle.dumps(feature_vec)
        f_feature.write(pickled_list)
        f_feature.close()
    else:
        f_abstract_dict = gzip.open(subdir + os.sep + subdir_basename + ".abstractcosine.gz","w")
        abstract_pickled_list = pickle.dumps(abstract_dict)
        f_abstract_dict.write(abstract_pickled_list)
        f_abstract_dict.close()
