#!/usr/bin/env python

import re
import sys
import psycopg2

from collections import Counter
from pyquery import PyQuery as pq

class DataClassifier:
	def __init__(self):
		self.connection = None
		self.cursor = None
		self.html = None
		self.type_map = dict()
		self.pq = pq
		self.sql_get_types = "SELECT id, type FROM tokens.type"
		self.sql_select = "SELECT token, type FROM tokens.all_tokens where token in ({token_list});"

	def connect(self, db_user, db_password, dbname, host, port=5432):
		try:
			self.connection = psycopg2.connect("dbname='{db_name}' host='{host}' user='{user_name}' password='{user_password}' port='{port}'".format(db_name=dbname,
																														host=host,
																														user_name=db_user,
																														user_password=db_password,
																														port=port))
			self.cursor = self.connection.cursor()
		except Exception as e:
			sys.stderr.write("Failed to connect to database\n")
			sys.stderr.write(str(e) + "\n")
		self.get_type_map()

	def disconnect(self):
		if self.connection:
			if self.cursor.closed == False:
				self.cursor.close()
			self.connection.close()
		

	def get_type_map(self):
		try:
			self.cursor.execute(self.sql_get_types)
			for item in self.cursor.fetchall():
				self.type_map.update({item[0]: item[1]})
		except Exception as e:
			sys.stderr.write("Failed to get token types\n")
			sys.stderr.write(str(e) + "\n")

	def current_elementname(self, pqobject):
		if pqobject:
			sys.stderr.write(str(pqobject))
			name = re.search(r"<([a-z]+)\s?", str(pqobject))
			if name:
				obj_name = name.group(1)
				obj_id = pqobject.attr("id")
				if obj_id:
					obj_name += "#" + obj_id
				obj_classes = pqobject.attr("class")
				if obj_classes:
					obj_name += "."
					obj_name += ".".join([obj_class for obj_class in obj_classes.split(" ")]) 
				
				return obj_name
			else:
				sys.stderr.write("No name matched: ")
				sys.stderr.write(str(pqobject) + "\n")
				return None
		else:
			sys.stderr.write("PyQuery object is empty")
			return None

	def classify(self, text):

		token_list = ""
		text = text.split()
		for i in range(len(text)):
			token_list += "'" + text[i].encode("utf-8").replace("'", "''") + "'"
			if i < len(text)-1:
				token_list += ","

		if token_list:
			self.cursor.execute(self.sql_select.format(token_list=token_list))
			text_type = Counter([item[1] for item in self.cursor.fetchall()]).most_common()
			text_type = text_type[0][0] if text_type and text_type[0][1] > len(text)/2 else None
			return text_type

	def recursive_classify(self, pqobject, output=[]):
		if self.connection is not None and self.cursor is not None:
			pqobject = pq(pqobject)
			output = list(output)

			_pqobject = pqobject.clone()
			_pqobject.children().remove()

			object_type = self.classify(_pqobject.text())
			object_name = self.current_elementname(_pqobject)
			if object_type and object_name:
				result = "type: " + str(object_type) + " content: " + _pqobject.text()

				if len(output) > 0:
					output.append({output[-1].keys()[0] + " " + object_name: result})
				else:
					output.append({object_name: result})

			_output = list(output)
			for child in pqobject.children():
				output += self.recursive_classify(child, _output)
			
			return output

		else:
			raise Exception("Not connected to database. You need to connect first!")

