#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import luigi

from data_scraper.scrape import start_crawling
from auto_scraper.tasks.start_url import StartUrlTask


class CrawlTask(luigi.Task):
	"""
	The task that takes the output from start_url Task 
	and crawls and returns just the urls you are interested in
	and not the web page data they lead to.
	"""
	config_parser = luigi.configuration.get_config()

	def requires(self):
		return StartUrlTask()

	def run(self):
		current_dir = os.getcwd()
		scrapers_folder = os.path.join(current_dir, "data_scraper/scrapers")
		sys.path.append(scrapers_folder)

		input_file = self.requires().output().path
		output_file = self.output().path

		with open(input_file) as crawl_input:
			with open(output_file, "w") as crawl_output:
				for line in crawl_input:
					request_object = json.loads(line)
					request_object["url"] = request_object.get("start_url")
					data = start_crawling(request_object)
					if data:
						crawl_output.write(json.dumps(data) + "\n")

	def output(self):
		output_folder = self.config_parser.get("jobs", "output_folder")
		job_date = self.config_parser.get("task_params", "date")
		job_output = self.config_parser.get("jobs", "CrawlTaskOutput")
		output = os.path.join(output_folder, job_date, job_output)
		return luigi.LocalTarget(output)

