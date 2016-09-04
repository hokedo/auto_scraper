#!/usr/bin/env python
#-*- coding:utf-8 -*-


import sys
import re
import pprint as pp
from urllib import unquote_plus
import requests

def requestPage(url):
	#s = requests.Session()
	#res = s.request("GET", url, verify=False)
	#return res.text.encode("utf-8")
	import os.path
	f = open(os.path.dirname(__file__) + "/../gen_test.html", "r")
	res = f.read()
	f.close()
	return res.decode('latin-1').encode("utf-8")

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
	