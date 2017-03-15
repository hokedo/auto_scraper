#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import luigi
import requests

from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectTimeout

from pyquery import PyQuery as pq
from auto_scraper.base import BaseTask

class ProxyTask(BaseTask):
	"""
	Find proxies to use for crawling
	"""
	headers = {
		'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',
	 	'Accept-Language': 'en-US,en;q=0.8,de-DE;q=0.6,de;q=0.4,en;q=0.2',
	 	'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16'
	 }

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
		self.logger.info("Requesting proxy list url:\t%s", url)
		table_row_selector = "#content table[align='center'][cellspacing='1'][cellpadding='3'] tr"
		response = requests.get(url, headers=self.headers, timeout=1, verify=False)
		doc = pq(response.text)
		for row in doc(table_row_selector):
			proxy_ip = pq(row).find('a[title="View this Proxy details"]').text()
			if proxy_ip and self.valid_proxy(proxy_ip):
				return proxy_ip

	def valid_proxy(self, proxy_address):
		self.logger.info("Testing proxy:\t%s", proxy_address)
		test_url = "http://httpbin.org/ip"
		proxies = {"http": proxy_address}
		try:
			response = requests.get(test_url, proxies=proxies, timeout=10, verify=False)
			ip = json.loads(response.text).get("origin")
			if ip == proxy_address:
				return True
		except (ConnectTimeout, ReadTimeout):
			self.logger.info("Proxy checker timed out on address:\t%s", proxy_address)
		except ValueError:
			self.logger.info("Invalid response from proxy checker on addres:\t%s", proxy_address)

		return False
