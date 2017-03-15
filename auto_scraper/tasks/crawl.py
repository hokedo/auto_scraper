#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import luigi

from auto_scraper.base import BaseTask
from data_scraper.scrape import start_crawling
from auto_scraper.tasks.get_proxy import ProxyTask
from auto_scraper.tasks.start_url import StartUrlTask


class CrawlTask(BaseTask):
	"""
	The task that takes the output from start_url Task 
	and crawls and returns just the urls you are interested in
	and not the web page data they lead to.
	"""
	config_parser = luigi.configuration.get_config()

	def requires(self):
		return {
			"proxy_task": ProxyTask(),
			"start_url": StartUrlTask()
		}

	def run(self):
		# Append system path with the folder for the crawlers/scrapers
		# It will be later needed by 'start_crawling'
		current_dir = os.getcwd()
		scrapers_folder = os.path.join(current_dir, "data_scraper/scrapers")
		sys.path.append(scrapers_folder)

		input_file = self.requires()["start_url"].output().path
		output_file = self.output().path
		proxies_file_path = self.requires()["proxy_task"].output().path

		with open(proxies_file_path) as proxies_file:
			proxies = json.loads(proxies_file.read())

		with open(input_file) as crawl_input:
			with open(output_file, "w") as crawl_output:
				for line in crawl_input:
					request_object = json.loads(line)
					request_object["url"] = request_object.get("start_url")
					for data in start_crawling(request_object, proxies):
						if data:
							crawl_output.write(json.dumps(data) + "\n")

	def output(self):
		job_output = self.config_parser.get("jobs", "CrawlTaskOutput")
		output = self.create_output_path(job_output)
		return luigi.LocalTarget(output)

