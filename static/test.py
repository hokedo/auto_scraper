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


MAIN_PAGE_TEMPLATE = {'properties': {'address': [{'path': 'Hotel Address', 'pp': ['text']}],
                'external_source_id': [{'path': 'External Id',
                                        'pp': ['text']}],
                'name': [{'path': 'div.container > div.detail-bg > div.page-sub.clearfix > div.hotel-top.clearfix > div.hotel-name > h1',
                          'pp': ['text']}],
                'score': [{'path': 'Hotel Score', 'pp': ['text']}]}}
REVIEW_TEMPLATE = {'properties': {'author': [{'path': 'Review Author', 'pp': ['text']}],
                'score': [{'path': 'Review Score', 'pp': ['text']}],
                'text': [{'path': 'div.comment-content.cm-md > p.ctext',
                          'pp': ['text']}]}}
REVIEW_PAGE_TEMPLATE = {"properties": {
							"review_list": {
								"path": 'div.container > div.detail-bg > div.page-sub.clearfix > div.page-cont.pad-r19.left > div#yorumlar.hotel-comment > div.paginated.clearfix > div.paginated-group > div.paginated-item.comment-element.br-3',
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
