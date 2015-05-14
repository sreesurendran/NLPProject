import nltk
import string, gzip, scipy
import os, sys
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer

if(len(sys.argv) < 3):
    print("USAGE: python create_tfidf.py <input_path> <feature> <OPT:restrict>")
    sys.exit()

input_path = sys.argv[1]
feature = sys.argv[2] + ".words"
stemmer = PorterStemmer()

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems

flag = False
if len(sys.argv) == 4:
    # restrictedFile = open('/Users/user/Desktop/Data/New/restricted.set', 'r')
    # restrictedSet = pickle.load (restrictedFile)
    # restrictedFile.close()
    restrictedSet = dict()
    restrictedSet[1] = ['C6']
    flag = True

fileList = []

for subdir, dirs, files in os.walk(input_path):
    for file in files:
        if file.endswith (feature):
            if flag:
                helper = subdir.split('/')
                cj = helper[-1]
                i = helper[-3]
                if cj not in restrictedSet.get(int(i), []):
                    continue
            file_path = subdir + os.path.sep + file
            shakes = open(file_path, 'r')
            fileList.append(shakes)

#Calculate tfidf
tfidf = TfidfVectorizer(input='file', decode_error='ignore', norm='l2',tokenizer=tokenize, stop_words='english',min_df=1)
tfidf.fit(fileList)
print "Size of Vocabulary:", len(tfidf.vocabulary_)
f_write = open("../vocabulary_" + sys.argv[2] + ".txt","w")
pickled_list = pickle.dumps(tfidf.vocabulary_)
f_write.write(pickled_list)
f_write.close()

for file in fileList:
    try:
        file.close()
    except:
        pass


for subdir, dirs, files in os.walk(input_path):
    for file in files:
        if file.endswith(feature):
            if flag:
                helper = subdir.split('/')
                cj = helper[-1]
                i = helper[-3]
                if cj not in restrictedSet.get(int(i), []):
                    continue
            file_path = subdir + os.path.sep + file
            shakes = open (file_path, 'r')
            f = gzip.open (file_path + '.tfidf.gz', 'w')
            vec = tfidf.transform ([shakes])
            f.write (pickle.dumps (vec))
            f.close()
            shakes.close()



