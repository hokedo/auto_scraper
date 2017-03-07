#!/usr/bin/env python
# coding: utf-8

import os
import json
import luigi
from auto_scraper.tasks.crawl import CrawlTask
from auto_scraper.base_psql_task import BasePsqlTask

class DeduplicationTask(BasePsqlTask):
	"""
	The task that queries the db for the start urls
	for each domain and generates the request object
	for the crawlers.
	"""

	def requires(self):
		return CrawlTask()

	def run(self):
		input_file = self.requires().output().path
		output_file = self.output().path

		self.get_connection()
		
		sql_file_path = self.config_parser.get("jobs", "SetDeleteFlagSql")
		with open(sql_file_path) as sql_file:
			self.cursor.execute(sql_file.read())

		sql_file_path = self.config_parser.get("jobs", "UpsertDataTemplate")
		with open(sql_file_path) as sql_file:
			upsert_query = sql_file.read()

		sql_file_path = self.config_parser.get("jobs", "InsertDataTemplate")
		with open(sql_file_path) as sql_file:
			insert_query = sql_file.read()

		with open(input_file) as input:
			with open(output_file, "w") as output:
				counter = 0
				url_list = []
				for line in input.readlines():
					data = json.loads(line.strip())
					url_list.append(data["url"])
					counter += 1


		self.cursor.close()
		self.connection.close()

	def output(self):
		output_folder = self.config_parser.get("jobs", "output_folder")
		job_date = self.config_parser.get("task_params", "date")
		job_output = self.config_parser.get("jobs", "DeplicationTaskOutput")
		output = os.path.join(output_folder, job_date, job_output)
		return luigi.LocalTarget(output)

	def key_value_split(self, dictionary):
		output = {"keys": [], "values": []}

		for key, value in dictionary.iteritems():
			output["keys"].append(key)
			output["values"].append(value)

		return output

	def sql_stringify_array(self, array):
		return repr(array).replace("]", "").replace("[", "")
