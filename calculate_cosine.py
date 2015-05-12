import os,sys
import numpy
from collections import OrderedDict
import pickle
from sklearn.metrics.pairwise import cosine_similarity

if(len(sys.argv) < 3):
    print("USAGE: python calculate_cosine.py <input_path> <feature>")
    sys.exit()

input_path = sys.argv[1].rstrip("/")
feature = sys.argv[2]

cx = lambda a, b : round(numpy.inner(a, b)/(numpy.linalg.norm(a)*numpy.linalg.norm(b)), 3)

#create the individual feature vector file
for subdir,dirs,files in os.walk(input_path):
    print("SUBDIR: %s" % subdir)
    if subdir == input_path:
        continue
    subdir_basename = os.path.basename(subdir)
    rep_file_path = subdir + os.sep + subdir_basename + ".rep." + feature
    if not os.path.isfile(rep_file_path):
        continue
    else:
        f_rep = open(rep_file_path,"r")
        rep_tfidf = pickle.load(f_rep)
        f_rep.close()
        feature_vec = OrderedDict()
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
                search_document_path = input_path + os.sep + search_document + os.sep + "cit"
                print("SEARCH DOCUMENT PATH: %s" % search_document_path)
                if os.path.isdir(search_document_path):
                    for inner_subdir, inner_dirs, inner_files in os.walk(search_document_path):
                        print("INNER SUBDIR: %s" % inner_subdir)
                        inner_subdir_basename = os.path.basename(inner_subdir)
                        for inner_file in inner_files:
                            inner_file_path = inner_subdir + os.sep + inner_file
                            print("INNER FILE PATH: %s" % inner_file_path)
                            tfidf_file_path = inner_subdir + os.sep + inner_subdir_basename + "_" + feature + ".words.tfidf"
                            if os.path.isfile(tfidf_file_path):
                                f_arg = open(tfidf_file_path,"r")
                                arg_tfidf = pickle.load(f_arg)
                                f_arg.close()
                                cosine = cx(rep_tfidf,arg_tfidf)
                                #cosine = cosine_similarity(
                                feature_vec[inner_subdir] = cosine
            feature_vec_file_path = subdir + os.sep + subdir_basename + "." + feature + ".feature"
            f_feature = open(feature_vec_file_path,"w")
            pickled_list = pickle.dumps(feature_vec)
            f_feature.write(pickled_list)
            f_feature.close()
