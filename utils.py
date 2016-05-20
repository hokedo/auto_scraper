import sys
import re
import pprint as pp
from urllib import unquote_plus
import requests

def requestPage(url):
	s = requests.Session()
	res = s.request("GET", url, verify=False)
	return res.text.encode("utf-8")

def get_parameters(url):
	output = {}
	hotel_items = []
	review_items = []
	review_frame = ""
	url = unquote_plus(url)
	parameters = url.split("&")
	parameters.pop(0) #remove the callback name
	parameters.pop() #remove the datestamp

	for item in parameters:
		item = item.split("=")
		selector = item[1]
		match = re.match(r"^(.+)\[(.+)\]$", item[0])
		sys.stderr.write(str(item) +'\n')
		if match:
			if match.group(1) == "hotel_items":
				hotel_items.append({match.group(2) : selector})
			elif match.group(1) == "review_items":
				review_items.append({match.group(2) : selector})
		elif item[0] == "review_frame":
			review_frame = selector
		elif item[0] == "page_url":
			page_url = item[1]
	output = {"hotel_items": hotel_items,
				"review_items": review_items,
				"review_frame": review_frame,
				"page_url": page_url}

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

	f = open("test.py", "w")
	f.write(headers + "\n" + imports + "\n" + main_page + "\n" + review_page + "\n" + review_frame + "\n\n" + footers + "\n")
	f.close()
