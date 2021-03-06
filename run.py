#!/usr/bin/env python
# coding: utf-8

import os
import luigi
import logging
import datetime

from argparse import ArgumentParser

from auto_scraper.tasks.get_proxy import ProxyTask
from auto_scraper.tasks.start_url import StartUrlTask
from auto_scraper.tasks.crawl import CrawlTask
from auto_scraper.tasks.update_db import UpdateDBTask
from auto_scraper.tasks.delete_data import DeleteOldDataTask
from auto_scraper.tasks.report import ReportTask
from auto_scraper.tasks.clean import CleanUpTask
from auto_scraper.tasks.geocode import GeocodeTask
from auto_scraper.tasks.populate_poi import PopulatePOITask

logging.config.fileConfig('config/logging.cfg')
logger = logging.getLogger()

def get_args():
	argp = ArgumentParser(__doc__)
	argp.add_argument(
		"--date",
		help="Date and hour for the current run.",
		default=datetime.datetime.now()
		)
	argp.add_argument(
		"--config",
		help="Name of the configuration file located in the 'config' folder",
		default="main"
		)
	argp.add_argument(
		"--poi",
		help="Run just the Points of interest populating Task",
		action="store_true",
		default=False
	)

	args = vars(argp.parse_args())
	return args

def format_date(date):
	date_format = config.get('core', 'date_format', '%Y-%m-%d_%H-%M')
	if not isinstance(date, basestring):
		return date.strftime(date_format)
	else:
		return date


if __name__ == "__main__":
	# Get CLI arguments
	args = get_args()

	config_path = os.path.join("config", "{}.cfg".format(args["config"]))
	logger.info("Loading config from %s", config_path)
	config = luigi.configuration.LuigiConfigParser.instance()
	config.add_config_path(config_path)

	# Add command line parameters
	config.set('task_params', 'date', format_date(args['date']))

	logger.info("Running with the following configuration:")
	for section in config.sections():
		logger.info("Section: %s", section)
		for k, v in config.items(section):
			logger.info("\t%s: %s", k, v)

	# Write the current configuration into 'luigi.cfg'
	# (default config file for luigi)
	# This config file will be used in case Tasks need
	# external parameters
	with open('luigi.cfg', 'w') as f:
		config.write(f)

	# Create output folder if it doesn't exist
	output_folder = config.get("jobs", "output_folder")
	if not os.path.isdir(output_folder):
		os.makedirs(output_folder)

	# Create folder for the current run if it doesn't exist
	current_date = config.get("task_params", "date")
	run_output = os.path.join(output_folder, current_date)
	if not os.path.isdir(run_output):
		os.makedirs(run_output)

	if args.get("poi"):
		tasks = [PopulatePOITask()]
	else:
		tasks = [
			ProxyTask(),
			StartUrlTask(),
			CrawlTask(),
			UpdateDBTask(),
			DeleteOldDataTask(),
			ReportTask(),
			CleanUpTask(),
			GeocodeTask()
		]

	luigi.interface.build(tasks, local_scheduler=True)
