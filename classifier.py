#!/usr/bin/env python
import sys
import psycopg2

from pyquery import PyQuery as pq

class DataClassifier:
	def __init__(self):
		self.connection = None
		self.cursor = None
		self.html = None
		self.type_map = {}
		self.pq = pq
		self.sql_get_types = "SELECT id, type FROM tokens.type"
		self.sql_select = "SELECT token, type FROM tokens.all_tokens where token in ({token_list});"

	def connect(self, db_user, db_password, dbname, host, port=5432):
		try:
			connection = psycopg2.connect("dbname='{db_name}' host='{host}' user='{user_name}' password='{user_password}'' port='{port}".format(db_name=dbname,
																														host=host,
																														user_name=db_user,
																														user_password=db_password,
																														port=port))
			self.connection = connection
			self.cursor = cursor = connection.cursor()
		except Exception as e:
			sys.stderr.write("Failed to connect to database\n")
			sys.stderr.write(str(e) + "\n")

	def disconnect(self):
		if self.connection:
			if self.cursor.closed == False:
				self.cursor.close()
			self.connection.close()
		


