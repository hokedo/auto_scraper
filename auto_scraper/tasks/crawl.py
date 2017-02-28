#!/usr/bin/env python
# coding: utf-8

import os
import json
import luigi
from auto_scraper.tasks.start_url import StartUrlTask


class CrawlTask(luigi.Task):
	"""
	The task that takes the output from start_url Task 
	and crawls and returns just the urls you are interested in
	and not the web page data they lead to.
	"""
	def requires(self):
		return [StartUrlTask()]

	def run(self):
		pass

	def output(self):
		output_folder = self.config_parser.get("jobs", "output_folder")
		job_date = self.config_parser.get("task_params", "date")
		job_output = self.config_parser.get("jobs", "CrawlTaskOutput")
		output = os.path.join(output_folder, job_date, job_output)
		return luigi.LocalTarget(output)

