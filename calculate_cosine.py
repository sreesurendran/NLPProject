import os,sys
import numpy, scipy
from collections import OrderedDict
import pickle
import gzip

if(len(sys.argv) < 3):
    print("USAGE: python calculate_cosine.py <input_path> <feature>")
    sys.exit()

input_path = sys.argv[1].rstrip("/")
feature = sys.argv[2]

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

#create the individual feature vector file
for subdir,dirs,files in os.walk(input_path):
    #print("SUBDIR: %s" % subdir)
    if subdir == input_path:
        continue
    subdir_basename = os.path.basename(subdir)
    if feature == "abstract":
        rep_file_path = subdir + os.sep + subdir_basename + ".abstract.words.tfidf.gz"
    else:
        rep_file_path = subdir + os.sep + subdir_basename + ".rep." + feature + ".gz"
    #print "REP FILE PATH: " + rep_file_path
    if not os.path.isfile(rep_file_path):
        continue
    else:
        f_rep = gzip.open(rep_file_path,"r")
        rep_tfidf = pickle.load(f_rep)
        f_rep.close()
        feature_vec = OrderedDict()
        abstract_dict = OrderedDict()
    for file in files:
        name,ext = os.path.splitext(file)
        search_list = []
        #first look at the inlinks
        #then look at the candidate set
        if ext == ".inlink":
            file_path = subdir + os.sep + file
            f_inlinks_candidates = open(file_path,"r")
            search_list.extend(f_inlinks_candidates.read().splitlines())
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
                search_document_path = input_path + os.sep + search_document + os.sep + "cit"
                #print("SEARCH DOCUMENT PATH: %s" % search_document_path)
                if os.path.isdir(search_document_path):
                    for inner_subdir, inner_dirs, inner_files in os.walk(search_document_path):
                        #print("INNER SUBDIR: %s" % inner_subdir)
                        inner_subdir_basename = os.path.basename(inner_subdir)
                        for inner_file in inner_files:
                            inner_file_path = inner_subdir + os.sep + inner_file
                            #print("INNER FILE PATH: %s" % inner_file_path)
                            tfidf_file_path = inner_subdir + os.sep + inner_subdir_basename + "_" + feature + ".words.tfidf.gz"
                            if os.path.isfile(tfidf_file_path):
                                f_arg = gzip.open(tfidf_file_path,"r")
                                arg_tfidf = pickle.load(f_arg)
                                f_arg.close()
                                cosine = get_cosine(rep_tfidf,arg_tfidf, feature)
                                feature_vec[inner_subdir] = cosine
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
