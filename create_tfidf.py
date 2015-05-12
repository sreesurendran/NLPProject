import nltk
import string
import os, sys
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from collections import OrderedDict

if(len(sys.argv) < 3):
    print("USAGE: python create_tfidf.py <input_path> <feature>")
    sys.exit()

input_path = sys.argv[1]
feature = sys.argv[2] + ".words"
token_dict = OrderedDict()
stemmer = PorterStemmer()

    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems

for subdir, dirs, files in os.walk(input_path):
    for file in files:
        if feature in file:
            file_path = subdir + os.path.sep + file
            print("YES: " + file_path)
            shakes = open(file_path, 'r')
            text = shakes.read()
            lowers = text.lower()
            no_punctuation = lowers.translate(None, string.punctuation)
            token_dict[file_path] = no_punctuation

#Calculate tfidf
tfidf = TfidfVectorizer(norm='l2',tokenizer=tokenize, stop_words='english',min_df=1)
tfs = tfidf.fit_transform(token_dict.values())
print "Vocabulary:", tfidf.vocabulary_
print tfs

ct = 0

#Write tfidf to file
for row in tfs.toarray():
    filename = token_dict.keys()[ct] + ".tfidf"
    pickled_list = pickle.dumps(row)
    f = open(filename,"w")
    #f.write(str(row))
    f.write(pickled_list)
    f.close()
    ct = ct + 1

#calculate the representative tfidf vector 
