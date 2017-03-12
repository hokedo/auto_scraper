#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import luigi
import requests

from pyquery import PyQuery as pq
from auto_scraper.base import BaseTask

class ProxyTask(BaseTask):
	"""
	Find proxies to use for crawling
	"""

	def run(self):
		output_file_path = self.output().path
		proxy_list_https = "http://www.xroxy.com/proxy--Anonymous--ssl.htm"
		proxy_list_http = "http://www.xroxy.com/proxy--Anonymous--nossl.htm" 
		proxies = {}

		http_proxy = self.get_proxy_ip(proxy_list_http)
		https_proxy = self.get_proxy_ip(proxy_list_https)

		if http_proxy and https_proxy:
			proxies = {
				"http": "http://{}".format(http_proxy),
				"https": "https://{}".format(https_proxy)
			}
			with open(output_file_path, "w") as output_file:
				output_file.write(json.dumps(proxies))
		else:
			raise Exception("No proxies found")

	def output(self):
		job_output = self.config_parser.get("jobs", "ProxyTaskOutput")
		output = self.create_output_path(job_output)
		return luigi.LocalTarget(output)

	def get_proxy_ip(self, url):
		table_row_selector = "#content table[align='center'][cellspacing='1'][cellpadding='3']"
		response = requests.get(url)
		doc = pq(response.text)
		for row in doc(table_row_selector):
			proxy_ip = pq(row).find('a[title="View this Proxy details"]').text()
			if self.valid_proxy(proxy_ip):
				return proxy_ip

	def valid_proxy(self, proxy_address):
		self.logger("Testing proxy:\t%s", proxy_address)
		test_url = "http://httpbin.org/ip"
		proxies = {"http": proxy_address}
		response = requests.get(test_url, proxies=proxies)
		try:
			ip = json.loads(response.text).get("origin")
			if ip == proxy_address:
				return True
		except ValueError:
			self.logger.info("%s\tNot valid proxy", proxy_address)

		return False
