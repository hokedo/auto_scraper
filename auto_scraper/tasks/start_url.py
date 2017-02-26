#!/usr/bin/env python
# coding: utf-8

import luigi
from auto_scraper.base_psql_task import BasePsqlTask


class StartUrlTask(BasePsqlTask):
	"""
	The task that queries the db for the start urls
	for each domain and generates the request object
	for the crawlers.
	"""
	def run(self):
		pass

