#!/usr/bin/env python

from pyquery import PyQuery as pq
import re

def dedup_dict_list(l):
	return [dict(t) for t in set([tuple(d.items()) for d in l])]

def current_elementname(pqobject):
	if pqobject:
		name = re.search(r"<([a-z]+)\s", str(pqobject))
		if name:
			obj_name = name.group(1)
			obj_id = pqobject.attr("id")
			if obj_id:
				obj_name += "#" + obj_id
			obj_classes = pqobject.attr("class")
			if obj_classes:
				obj_name += "."
				obj_name += ".".join([obj_class for obj_class in obj_classes.split(" ")]) 
			
			return obj_name
		else:
			print "No name matched"
			return None
	else:
		print "PyQuery object is empty"
		return None

def recursive_classify(pqobject, output=[]):
	pqobject = pq(pqobject)
	output = list(output)

	_pqobject = pqobject.clone()
	_pqobject.children().remove()
	result = _pqobject.text()
	if len(output) > 0:
		output.append({output[-1].keys()[0] + " " + current_elementname(_pqobject): result})
	else:
		output.append({current_elementname(_pqobject): result})

	_output = list(output)
	for child in pqobject.children():
		output += recursive_classify(child, _output)
	
	return output


f = open("gen_test.html", "r")
h = pq(f.read())
f.close()
a = h("p.name:eq(0)")
b = recursive_classify(a)
print dedup_dict_list(b)
