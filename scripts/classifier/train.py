#!/usr/bin/env python
import json
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
	token = token.strip()
	if token.isdigit():
		return "NUM"
	return token.lower()

def bow(text):
	"""
	Bag of words.
	"""
	return {normalize(token): True for token in set(text.split())}

def asd(a):
	print a
	return a

if __name__ == "__main__":
	labels = []
	for line in sys.stdin:
		data = json.loads(line.strip())
		for key, value in data.iteritems():
			if value:
				labels.append((value, key))
	a = [(bow(text), label) for text, label in labels]
	m = MaxentClassifier.train(a)
	pwrite(m)
	print m.classify(bow("Hotel Las Vegas"))
	print m.classify((bow("Cluj-Napoca")))
	print m.classify((bow("decomandat")))
	print m.classify((bow("altceva")))
	print m.classify((bow("500 EUR")))