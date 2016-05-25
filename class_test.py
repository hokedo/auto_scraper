#!/usr/bin/env python

from pyquery import PyQuery as pq

def recursive_classify(pqobject):
	pqobject = pq(pqobject)
	for child in pqobject.children():
		recursive_classify(child)

	_pqobject = pqobject.clone()
	_pqobject.children().remove()
	print _pqobject.text(), "\n", "---------------------------------------------"

f = open("gen_test.html", "r")
h = pq(f.read())
f.close()
a = h("p.name:eq(0)")
recursive_classify(a)
