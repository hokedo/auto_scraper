#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import luigi
import requests

from urlparse import urljoin

from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectTimeout

from pyquery import PyQuery as pq
from auto_scraper.base_psql_task import BasePsqlTask

class ProxyTask(BasePsqlTask):
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
		proxies = {}

		http_proxy = self.get_proxy_ip(protocol="http")
		https_proxy = self.get_proxy_ip(protocol="https")

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

	def get_proxy_ip(self, protocol):
		query_file_path = self.config_parser.get("jobs", "GetProxySql")
		with open(query_file_path) as query_file:
			query = query_file.read()
			
		self.get_connection()
		self.cursor.execute(query)
		for row in self.cursor:
			data = dict(row)
			if protocol == data["protocol"]:
				proxy_address = data["ip"] + ":" + str(data["port"])
				if self.valid_proxy(proxy_address):
					self.connection.close()
					return proxy_address

	def valid_proxy(self, proxy_address):
		self.logger.info("Testing proxy:\t%s", proxy_address)
		test_url = "http://httpbin.org/ip"
		proxies = {"http": proxy_address}
		try:
			response = requests.get(test_url, proxies=proxies, timeout=10, verify=False)
			ip = json.loads(response.text).get("origin")
			if ip == proxy_address.split(":")[0]:
				return True
		except (ConnectTimeout, ReadTimeout):
			self.logger.info("Proxy checker timed out on address:\t%s", proxy_address)
		except ValueError:
			self.logger.info("Invalid response from proxy checker on address:\t%s", proxy_address)
			self.logger.info(response.text)
		except Exception as e:
			self.logger.warn("ProxyTask Exception:\t%s", str(e))

		return False
