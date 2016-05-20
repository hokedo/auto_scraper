#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import json
import logging

from pyquery import PyQuery as pq

import extract_util

logger = logging.getLogger("xxx.yyy.data")
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d - %(message)s")
logging.getLogger("extract.util").setLevel(logging.INFO)


MAIN_PAGE_TEMPLATE = {'properties': {}}
REVIEW_TEMPLATE = {'properties': {}}
REVIEW_PAGE_TEMPLATE = {"properties": {
							"review_list": {
								"path": ' ',
								"items": REVIEW_TEMPLATE
						}
					}
				}


def extract_data(req):
doc = pq(req['html'])
result = {}

for template in [MAIN_PAGE_TEMPLATE, REVIEW_PAGE_TEMPLATE]:
	extracted_data = extract_util.extract(doc, template, req['url'])
	logger.debug("extracted: \n%s", json.dumps(extracted_data, indent=2))

	if extracted_data:
		result.update(extracted_data)

return result


if __name__ == '__main__':

for line in sys.stdin:
	req = json.loads(line)
	data = extract_data(req)
	json.dump(data, sys.stdout)
