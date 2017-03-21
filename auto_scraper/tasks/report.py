#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import luigi

from auto_scraper.base import BaseTask
from auto_scraper.tasks.update_db import UpdateDBTask
from auto_scraper.tasks.delete_data import DeleteOldDataTask


class ReportTask(BaseTask):
	"""
	Generate a small report with all insertions and deletions
	"""

	def requires(self):
		return DeleteOldDataTask()

	def run(self):
		input_file = self.requires().output().path
		output_file = self.output().path
		inserted_data_file = UpdateDBTask().output().path
		slack_hook_path = os.path.expanduser('~/.slack_hook')

		with open(input_file) as input:
			report_data = {}
			report_data["domain_deletions"] = json.loads(input.read())
			report_data["total_deleted"] = sum([item.get("count", 0) for item in report_data["domain_deletions"]])
			with open(inserted_data_file) as inserted_data:
				report_data["domain_inserts"] = {}
				counter = 0
				for line in inserted_data:
					url, domain = line.strip().split("\t")
					if domain in report_data["domain_inserts"]:
						report_data["domain_inserts"][domain] += 1
					else:
						report_data["domain_inserts"][domain] = 1
					counter += 1
			report_data["total_inserts"] = counter

			with open(output_file, "w") as output:
				output.write(json.dumps(report_data))

		if os.path.isfile(slack_hook_path):
			# **optional**
			# Send yourself a message to slack 
			# containing the report data
			import requests
			with open(slack_hook_path) as slack_hook_file:
				slack_hook = slack_hook_file.read().strip()

			requests.post(
							slack_hook,
							json={
	            				"text": "Auto Scraper Report: {}".format(report_data),
	    					}
	    				)

	def output(self):
		job_output = self.config_parser.get("jobs", "ReportTaskOutput")
		output = self.create_output_path(job_output)
		return luigi.LocalTarget(output)
