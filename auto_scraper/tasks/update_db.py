#!/usr/bin/env python
# coding: utf-8

import os
import json
import luigi

from auto_scraper.tasks.crawl import CrawlTask
from auto_scraper.base_psql_task import BasePsqlTask

from psycopg2 import InternalError
from psycopg2 import IntegrityError
from psycopg2 import ProgrammingError

class UpdateDBTask(BasePsqlTask):
	"""
	Set the 'to_be_deleted' flag to true for all urls.
	The primary key of the table, where the crawled data is stored,
	is the url. Add the data just if the url doesn't already exist.
	If it exists, reset the 'to_be_deleted' flag.
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

		sql_file_path = self.config_parser.get("jobs", "ResetFlagTemplate")
		with open(sql_file_path) as sql_file:
			reset_query = sql_file.read()

		sql_file_path = self.config_parser.get("jobs", "InsertDataTemplate")
		with open(sql_file_path) as sql_file:
			insert_query = sql_file.read()

		# I know that I'm redefining the built-in
		# 'input'. Couldn't get any more creative
		# for the name of this variable
		with open(input_file) as input:
			with open(output_file, "w") as output:
				for line in input.readlines():
					data = json.loads(line.strip())
					if data.get("data"):
						data["data"]["url"] = data["url"]
						data["data"]["domain"] = data["domain"]
						to_insert = self.key_value_split(data["data"])

						# Not really happy with this part
						keys = self.sql_stringify_array(to_insert["keys"]).replace("u'", "").replace("'", "")
						values = self.sql_stringify_array(to_insert["values"]).replace("u'", "'")

						try:
							self.cursor.execute(insert_query.format(keys=keys, values=values))

						except IntegrityError as e:
							# Exception thrown in case
							# constraints are violated
							self.logger.warn(str(e))
							self.connection.rollback()
							# Key (url) already exists
							# Reset the flag so that this 
							# entry doesn't get deleted
							self.cursor.execute(reset_query.format(data["url"]))

						except (ProgrammingError, InternalError) as e:
							self.logger.error(str(e))
							self.logger.error(json.dumps(data["data"]))
							continue

						self.connection.commit()
						output.write("{}\t{}\n".format(data["url"], data["domain"]))

		self.cursor.close()
		self.connection.close()

	def output(self):
		job_output = self.config_parser.get("jobs", "DeplicationTaskOutput")
		output = self.create_output_path(job_output)
		return luigi.LocalTarget(output)

	def key_value_split(self, dictionary):
		output = {"keys": [], "values": []}

		for key, value in dictionary.iteritems():
			output["keys"].append(key)
			output["values"].append(value)

		return output

	def sql_stringify_array(self, array):
		return repr(array).replace("]", "").replace("[", "")
