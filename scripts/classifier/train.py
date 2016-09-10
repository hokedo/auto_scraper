#!/usr/bin/env python

import sys
import pickle
from nltk.classify.maxent import MaxentClassifier
"""
Input training data and save a classifier to a file using pickle
"""
labels = [
	("Hotel Las Vegas", "HOTEL_NAME"),
	("Opera Plaza Hotel", "HOTEL_NAME"),
	("10 Angelina Street", "HOTEL_ADDRESS"),
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



if __name__ == "__main__":
	labels = []
	for line in sys.stdin:
		#input format: text \t label
		data = line.strip().split("\t")
		data = tuple(data)
		labels.append(data)
	m = MaxentClassifier.train([(bow(text), label) for text, label in labels])
	pwrite(m)

