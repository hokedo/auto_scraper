#!/usr/bin/env python

from nltk.classify.maxent import MaxentClassifier
import pickle

labels = [
	("Hotel Las Vegas", "HOTEL"),
	("Opera Plaza Hotel", "HOTEL"),
	("10 Angelina Street", "ADDRESS"),
]

def pread():
	f = open("classifier.pickle", "r")
	classifier =  pickle.load(f)
	f.close()
	return classifier

def pwrite(classifier):
	f = open("classifier.pickle", "w")
	pickle.dump(classifier, f)
	f.close()

def normalize(token):
	if token.isdigit():
		return "NUM"
	return token.lower()

def bow(text):
	"""
	Bag of words.
	"""
	return {normalize(token): True for token in set(text.split())}

m = MaxentClassifier.train([(bow(text), label) for text, label in labels])



# print m.classify(bow("Hotel Las Vegas"))
# print m.classify(bow("d"))
# print m.explain(bow("adidas"))
