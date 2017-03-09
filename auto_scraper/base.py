#!/usr/bin/env python
# coding: utf-8

import os
import luigi
import logging

class BaseTask(luigi.Task):
	"""
	Task that is going to be inherited by all
	other tasks
	"""
	config_parser = luigi.configuration.get_config()
	logger = logging.getLogger()

	def create_output_path(self, job_output):
		output_folder = self.config_parser.get("jobs", "output_folder")
		job_date = self.config_parser.get("task_params", "date")

		return os.path.join(output_folder, job_date, job_output)
