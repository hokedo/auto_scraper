#!/usr/bin/env python
# coding: utf-8

import json
import luigi

from auto_scraper.base_psql_task import BasePsqlTask
from auto_scraper.tasks.update_db import UpdateDBTask


class DeleteOldDataTask(BasePsqlTask):
	"""
	Delete entries that were flagged in the previous task
	"""

	def requires(self):
		return UpdateDBTask()

	def run(self):
		output_file = self.output().path
		sql_file_path = self.config_parser.get("jobs", "CountFlaggedData")
		with open(sql_file_path) as sql_file:
			count_flagged_query = sql_file.read()

		sql_file_path = self.config_parser.get("jobs", "DeleteFlaggedData")
		with open(sql_file_path) as sql_file:
			delete_flagged_query = sql_file.read()

		self.get_connection()
		# Count number of entries that are
		# going to be deleted per domain
		# It's going to be later used to 
		# generate the report
		self.cursor.execute(count_flagged_query)
		with open(output_file, "w") as output:
			count = {}
			for row in self.cursor.fetchall():
				count.update(dict(row))
			output.write(json.dumps(count) + "\n")

		self.cursor.execute(delete_flagged_query)
		affected_rows = self.cursor.rowcount
		self.logger.info("Deleted %d entries from database", affected_rows)

		self.cursor.close()
		self.connection.close()

	def output(self):
		job_output = self.config_parser.get("jobs", "DeleteOldDataTaskOutput")
		output = self.create_output_path(job_output)
		return luigi.LocalTarget(output)

