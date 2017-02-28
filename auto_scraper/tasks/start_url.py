#!/usr/bin/env python
# coding: utf-8

import os
import json
import luigi
from auto_scraper.base_psql_task import BasePsqlTask


class StartUrlTask(BasePsqlTask):
	"""
	The task that queries the db for the start urls
	for each domain and generates the request object
	for the crawlers.
	"""

	def run(self):
		sql_file_path = self.config_parser.get("jobs", "StartUrlTaskSql")
		with open(sql_file_path) as sql_file:
			query = sql_file.read()

		
		with open(self.output().path, "w") as output:
			self.cursor.execute(query)
			for row in self.cursor.fetchall():
				request = dict(row)
				output.write(json.dumps(request) + "\n")

		self.cursor.close()
		self.connection.close()

	def output(self):
		output_folder = self.config_parser.get("jobs", "output_folder")
		job_date = self.config_parser.get("task_params", "date")
		job_output = self.config_parser.get("jobs", "StartUrlTaskOutput")
		output = os.path.join(output_folder, job_date, job_output)
		return luigi.LocalTarget(output)

