#!/usr/bin/env python
#-*- coding:utf-8 -*-


import sys
import re
import pprint as pp
from urllib import unquote_plus
import requests

color_codes = {
	"HOTEL_NAME": "highlighted-green",
	"HOTEL_ADDRESS": "hotel_address",
	"REVIEW_TEXT": "highlighted-gray",
	"REVIEW_TITLE": "highlighted-black",
	"REVIEW_AUTHOR": "review_red",
	"REVIEW_DATE": "review_date",
	"REVIEW_SCORE": "highlighted-orange"
}

def requestPage(url):
	#s = requests.Session()
	#res = s.request("GET", url, verify=False)
	#return res.text.encode("utf-8")
	import os.path
	f = open(os.path.dirname(__file__) + "/../gen_test.html", "r")
	res = f.read()
	f.close()
	return res.decode('latin-1').encode("utf-8")

def requestProccesedPage(url, classifier):
	#s = requests.Session()
	#res = s.request("GET", url, verify=False)
	#return res.text.encode("utf-8")
	import os.path
	f = open(os.path.dirname(__file__) + "/../gen_test.html", "r")
	res = f.read()
	f.close()
	res = res.decode('latin-1').encode("utf-8")
	selectors = classify(res, classifier)
	final_selectors = filterSelectors(res, selectors)
	res = highlightText(res)

	return res, final_selectors

def filterSelectors(html, selectors):
	from pyquery import PyQuery as pq
	h = pq(html)
	result = {}
	# filter hotel title
	if selectors.get("HOTEL_NAME"):
		result["HOTEL_NAME"] = []
		for i in range(len(selectors["HOTEL_NAME"])):
			selector = selectors["HOTEL_NAME"][i]
			if len(h(selector)) == 1 and not containsOthers(selector, selectors["HOTEL_NAME"], h):
				if isDuplicate(selector, selectors["HOTEL_NAME"], h):
					result["HOTEL_NAME"] = [selector]
					break
				result["HOTEL_NAME"].append(selector)
		result["HOTEL_NAME"] = randomElement(result["HOTEL_NAME"])
	# filter review text and author
	if selectors.get("REVIEW_TEXT"):
		all_other_selectors = []
		for key, value in selectors.items():
			if key != "REVIEW_TEXT":
				all_other_selectors += value
		found = False
		for key in ["REVIEW_AUTHOR", "REVIEW_DATE", "REVIEW_SCORE"]:
			if key in selectors:
				for text_selector in selectors.get("REVIEW_TEXT"):
					if containsOthers(text_selector, all_other_selectors, h):
						for other_selector in selectors.get(key):
							text_count = len(h(text_selector))
							other_count = len(h(other_selector))
							if ((text_count == other_count > 1) and  
								underSameFrame(text_selector, other_selector, h)):
								#let's assume that there isn't just one review
								result["REVIEW_TEXT"] = text_selector
								result[key] = other_selector
								found = True
								break
					if found:
						break
			if found:
				break
	return result

def underSameFrame(selector1, selector2, pq_class, max_level=3):
	parent = pq_class(selector1).parent()
	current_level = 0
	while current_level < max_level:
		if parent.find(selector2):
			return True
		current_level += 1
		parent = parent.parent()
	return False

def randomElement(item_list):
	from random import choice
	return choice(item_list)

def isDuplicate(item, others, pq_class):
	_item = pq_class(item)
	for other in others:
		_other = pq_class(other)
		if _other.text() == _item.text():
			return True
	return False

def containsOthers(item, others, pq_class):
	_item = pq_class(item)
	for other in others:
		_other = pq_class(other)
		if _other.text() in _item.text() and _other.text() != _item.text():
			return True
	return False

def highlightText(html):
	from pyquery import PyQuery as pq
	def highlight(PqObject, pq_class=pq, highlight_color="highlighted-blue"):
		#highlight the selectable text in blue if you hover over it
		if NodeText(PqObject):
			PqObject.addClass(highlight_color)
			PqObject.addClass("SpecialClickable")
		for child in PqObject.children():
			highlight(pq_class(child), pq_class)
	h = pq(html)
	h("a").attr("href", "")
	highlight(h("body"), h)
	return h.html()

def classify(html, classifier):
	from pyquery import PyQuery as pq
	def _classify(PqObject, selectors):
		text = PqObject.text().strip()
		if text:
			text_type = classifier.classify(bow(text))
			selector = getPath(PqObject)
			if selector:
				if selectors.get(text_type):
					if selector not in selectors[text_type]:
						selectors[text_type].append(selector)
				else:
					selectors[text_type] = [selector]
		for child in PqObject.children():
			_classify(pq(child), selectors)			
	h = pq(html)
	selectors = {}
	_classify(h("body"), selectors)
	return selectors

def getPath(PqObejct, path="", recursive_depth=0, max_recursive_depth=5):
	if recursive_depth < max_recursive_depth:
		match = re.match(r"\[<(.+)>\]", repr(PqObejct))
		if match:
			path = match.group(1) + " " + path
			return (getPath(PqObejct.parent(), path, recursive_depth+1) or "").replace(". ", " ").strip()
	else:
		return path

def NodeText(PqObejct):
	#check if the element contains text without taking the children into account
	node = PqObejct.clone()
	node.children().remove()
	if len(node.text().strip()):
		return node.text()
	else: 
		return False

def get_parameters(url):
	sys.stderr.write("Recieved url: "+ str(url) + "\n")
	output = {}
	url = unquote_plus(url)
	parameters = url.split("&")

	for item in parameters:
		sys.stderr.write("Item:" + str(item) + '\n')
		item = item.split("=")
		selector = item[1] if item and len(item) > 1 else ''
		match = re.match(r"^(.+)\[(.+)\]$", item[0])
		if match:
			if match.group(1) in output.keys():
				output[match.group(1)].append({match.group(2) : selector})
			else:
				output[match.group(1)] = [{match.group(2) : selector}]
		else:
			output[item[0]] = selector
	
	return output

def create_files(parameters):
	#Generate data crawler
	headers = "".join(["#!/usr/bin/env python\n",
						"#-*- coding:utf-8 -*-\n",
						
						])
	imports = "".join(["import sys\n",
						"import json\n",
						"import logging\n",
						"\n",
						"from pyquery import PyQuery as pq\n",
						"\n",
						"import extract_util\n",
						"\n",
						"logger = logging.getLogger(\"xxx.yyy.data\")\n",
						"logging.basicConfig(level=logging.INFO, stream=sys.stderr, format=\"%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d - %(message)s\")\n",
						"logging.getLogger(\"extract.util\").setLevel(logging.INFO)\n"
						"\n",
						])

	main_page = {"properties": 
					dict((item.keys()[0], [{"path": item.values()[0], "pp": ["text"]}]) for item in parameters.get("hotel_items", []))
				}
	main_page = "MAIN_PAGE_TEMPLATE = " + pp.pformat(main_page)			

	review_page = {"properties": 
					dict((item.keys()[0], [{"path": item.values()[0], "pp": ["text"]}]) for item in parameters.get("review_items", []))
				}
	review_page = "REVIEW_TEMPLATE = " + pp.pformat(review_page)

	review_frame = ("REVIEW_PAGE_TEMPLATE = " + 
	 		  '{"properties": {\n' +	
	 '\t'*7 + '"review_list": {\n' +
	 '\t'*8 + '"path": \'' + (str(parameters.get("review_frame")) or " ") + "',\n" +
	 '\t'*8 + '"items": REVIEW_TEMPLATE\n' +
	 '\t'*6 + '}\n' +
	 '\t'*5 + '}\n' +
	 '\t'*4 + '}\n')

	footers = """def extract_data(req):
	doc = pq(req['html'])
	result = {}

	for template in [MAIN_PAGE_TEMPLATE, REVIEW_PAGE_TEMPLATE]:
		extracted_data = extract_util.extract(doc, template, req['url'])
		logger.debug("extracted: \\n%s", json.dumps(extracted_data, indent=2))

		if extracted_data:
			result.update(extracted_data)

	return result


if __name__ == '__main__':

	for line in sys.stdin:
		req = json.loads(line)
		data = extract_data(req)
		json.dump(data, sys.stdout)"""

	f = open("./static/test.py", "w")
	f.write(headers + "\n" + imports + "\n" + main_page + "\n" + review_page + "\n" + review_frame + "\n\n" + footers + "\n")
	f.close()

def stripper(string, strippers):
	flag = True
	while flag:
		flag = False
		if len(string) > 0 and string[0] in strippers:
			string = string.strip(string[0])
			flag = True
		if len(string) > 0 and string[-1] in strippers:
			string = string.strip(string[-1])
			flag = True
	return string

def filter_range(string, char_range):
	for character in string:
		if ord(character) < char_range[0] or ord(character) > char_range[-1]:
			return False
	return True

def splitter(string):
	if "　" in string:
		return string.split("　")
	else:
		return string.split()

def mapper_process(line, args):
	line = line.strip().split("\t")
	if len(line) >= hdfs_mapping[args.type] and line[hdfs_mapping[args.type]] is not None and line[hdfs_mapping[args.type]] != '':
		title = line[hdfs_mapping[args.type]]
		for token in splitter(title):
			_token = stripper(token, strippers)
			if filter_range(_token, char_range):
				print _token

insert_mapping = { 
	"review_text" : 2,
	"hotel_title" : 1
}
hdfs_mapping = { #HDFS tsv files
	"review_text" : 10, #from hotel4x.reivew
	"hotel_title" : 9 #from hotel4x.source
	}
strippers = [" ", ";", ".", ",", "`", "'", "/", "\\", ")", "(", "-", "[", "]", "/", "&", "*"]
char_range = [0, 127]


def dedup_dict_list(l):
	return [dict(t) for t in set([tuple(d.items()) for d in l])]

def normalize(token):
	if token.isdigit():
		return "NUM"
	return token.lower()

def bow(text):
	"""
	Bag of words.
	"""
	return {normalize(token): True for token in set(text.split())}
	