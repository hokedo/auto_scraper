
import os
import sys
import json
import luigi
import shutil
from auto_scraper.base import BaseTask

class CleanUpTask(BaseTask):
	"""
	Delete output folders from previous runs
	Keep just the last n (configured in the
	config file) runs.
	"""

	def run(self):
		output_file_path = self.output().path
		total_runs = int(self.config_parser.get("jobs", "keep_runs"))
		output_folder = self.config_parser.get("jobs", "output_folder")

		if total_runs and total_runs > 0:
			runs = sorted(os.listdir(output_folder))
			with open(output_file_path, "w") as output_file:
				while total_runs < len(runs):
					oldest_run = runs.pop(0)
					oldest_run_path = os.path.join(output_folder, oldest_run)
					shutil.rmtree(oldest_run_path)
					output_file.write(oldest_run_path + "\n")
		else:
			open(output_file_path, "w").close()

	def output(self):
		job_output = self.config_parser.get("jobs", "CleanUpTaskOutput")
		output = self.create_output_path(job_output)
		return luigi.LocalTarget(output)