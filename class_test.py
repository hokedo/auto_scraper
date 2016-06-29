#!/usr/bin/env python

import sys
import json
from scripts.utils import dedup_dict_list
from pyquery import PyQuery as pq
from scripts.classifier import DataClassifier

classifier = DataClassifier()
classifier.connect("dev-ro", "password", "ty_temp", "127.0.0.1", "5433")
f = open("gen_test.html", "r")
#h = pq(f.read())
h = pq("http://stackoverflow.com/questions/2600191/how-can-i-count-the-occurrences-of-a-list-item-in-python")
f.close()
#a = h("p.name:eq(0)")
a = h("body")
#b = recursive_classify(a)
#print dedup_dict_list(b)
sys.stdout.write(json.dumps(dedup_dict_list(classifier.recursive_classify(a))))
