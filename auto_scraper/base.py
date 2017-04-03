#!/usr/bin/env python
# coding: utf-8

import os
import luigi
import logging
import requests
logging.config.fileConfig('config/logging.cfg')

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

	def slack_hook(self, message):
		slack_hook_path = self.config_parser.get("slack", "hook")
		slack_hook_path = os.path.expanduser(slack_hook_path)
		if os.path.isfile(slack_hook_path):
			with open(slack_hook_path) as slack_hook_file:
				slack_hook = slack_hook_file.read().strip()

			requests.post(
				slack_hook,
				json={
					"username": "AutoScraper",
					"icon_emoji": ":spider:",
					"text": "Auto Scraper Report: {}".format(message),
				}
			)
		else:
			self.logger.warning("No Slack hook found at: %s", slack_hook_path)