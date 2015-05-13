import sys, os, scipy
import pickle
import numpy
import gzip

if(len(sys.argv) < 4):
    print("USAGE: python generate_rep.py <input_path> <feature> <decision_tree_path>")
    sys.exit()

input_path = sys.argv[1].rstrip("/")
feature = sys.argv[2]
decision_tree_path = sys.argv[3]

f_decision_trees = open(decision_tree_path,"r")
decision_tree_list = f_decision_trees.read().splitlines()
f_decision_trees.close()

totCount = 0

#calculate the representative tfidf vector
for subdir, dirs, files in os.walk(input_path):
    tfidf_values = []
    # print("SUBDIR: %s" % subdir)
    if totCount % 4000 == 0:
        print totCount
    totCount += 1
    subdir_basename = os.path.basename(subdir)
    if subdir_basename not in decision_tree_list:
        continue
    for file in files:
        name,ext = os.path.splitext(file)
        if ext == ".inlink":
            file_path = subdir + os.sep + file
            f = open(file_path,"r")
            inlinks = f.read().splitlines()
            f.close()
            for inlink in inlinks:
                inlink_path = input_path + os.sep + inlink + os.sep + "cit"
                # print("INLINK PATH: %s" % inlink_path)
                if os.path.isdir(inlink_path):
                    for inner_subdir, inner_dirs, inner_files in os.walk(inlink_path):
                        # print("INNER SUBDIR: %s" % inner_subdir)
                        inner_subdir_basename = os.path.basename(inner_subdir)
                        for inner_file in inner_files:
                            inner_name,inner_ext = os.path.splitext(inner_file)
                            inner_file_path = inner_subdir + os.sep + inner_file
                            if inner_ext == ".list":
                                f_inner = open(inner_file_path,"r")
                                documents_cited = f_inner.read().splitlines()
                                f_inner.close()
                                tfidf_zip_file_path = inner_subdir + os.sep + inner_subdir_basename + "_" + feature + ".words.tfidf.gz"
                                if (subdir_basename in documents_cited) and (os.path.isfile(tfidf_zip_file_path)):
                                    tfidf_file = gzip.open(tfidf_zip_file_path,"r")
                                    read_tfidf_file = tfidf_file.read()
                                    tfidf_values.append(pickle.loads(read_tfidf_file))
                                    tfidf_file.close()
    if len(tfidf_values) > 0:
        sum_tfidf = scipy.sum(tfidf_values)
        avg_tfidf = sum_tfidf/len(tfidf_values)
        rep_filename = subdir + os.sep + subdir_basename + ".rep." + feature + ".gz"
        # print("RE_PATH: " + rep_filename)
        f_rep = gzip.open(rep_filename,"w")
        pickled_list = pickle.dumps(avg_tfidf)
        f_rep.write(pickled_list)
        f_rep.close()

