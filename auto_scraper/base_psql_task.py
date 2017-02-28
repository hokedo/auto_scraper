#!/usr/bin/env python
# coding: utf-8

import os
import luigi
import logging
import psycopg2
import psycopg2.extras

logger = logging.getLogger()

class BasePsqlTask(luigi.Task):
	"""
	Base Task Class if you need to query the database
	Don't forget to close self.connection after all the
	querying is finished!!!
	"""
	def __init__(self):
		super(BasePsqlTask, self).__init__()
		self.config_parser = luigi.configuration.get_config()
		self.port = self.config_parser.getint("db", "port")
		self.host = self.config_parser.get("db", "host")
		self.database = self.config_parser.get("db", "database")
		self.username = self.config_parser.get("db", "username")
		self.password = self.pgpass()
		self.get_connection()

	def run(self):
		pass

	def get_connection(self):
		"""
		Create a db connection. If connection is successful,
		it is saved inside the object alongside with the cursor.
		"""
		self.connection = psycopg2.connect(
										dbname=self.database,
										user=self.username,
										password=self.password,
										host=self.host,
										port=self.port
										)
		self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

	def pgpass(self):
		"""
		Read the password, for the db connection, in the
		user's "pgpass" file located in the root of the
		home folder.
		"""
		pgpass_path = os.path.expanduser('~/.pgpass')
		with open(pgpass_path) as f:
			for line in f:
				host, port, _, user, passwd = line.split(':')
				if host == self.host and user == self.username:
					return passwd.strip()

		error_msg = "Could not find password for user {} is ~/.pgpass".format(self.username)
		raise ValueError(error_msg)