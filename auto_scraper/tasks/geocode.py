import json
import luigi
import requests

from urllib import quote_plus

from auto_scraper.base_psql_task import BasePsqlTask
from auto_scraper.tasks.update_db import UpdateDBTask

class GeocodeTask(BasePsqlTask):
	"""
	Generate geocoordinates using the address
	"""
	def requires(self):
		return UpdateDBTask()

	def run(self):
		output_file_path = self.output().path
		get_address_query_path = self.config_parser.get("jobs", "GetAddressesSql")
		insert_coord_query_path = self.config_parser.get("jobs", "InsertCoordSqlTemplate")
		api_key = self.config_parser.get("api_keys", "maps_api")
		api_url = self.config_parser.get("jobs", "GoogleMapsApi")
		inserts = []

		with open(get_address_query_path) as get_address_query_file:
			get_address_query = get_address_query_file.read().strip()

		with open(insert_coord_query_path) as insert_coord_query_file:
			insert_coord_query = insert_coord_query_file.read().strip()

		self.get_connection()
		self.cursor.execute(get_address_query)


		for row in self.cursor.fetchall():
			row = dict(row)
			address = quote_plus(row["address"])
			self.logger.info("Requesting for address:\t%s", address)
			response = requests.get(api_url.format(
				quoted_address=address,
				key=api_key)
			)
			data = json.loads(response.text)
			if data.get("results") and len(data["results"]):
				data = data.get("results")[0]
				latitude = data.get("geometry", {}).get("location", {}).get("lat")
				longitude = data.get("geometry", {}).get("location", {}).get("lng")
				insert_data = {
					"address": row["address"],
					"longitude": longitude,
					"latitude": latitude
				}
				inserts.append(insert_data)
			else:
				self.logger.warning("Skipped address: %s", address)

		with open(output_file_path, "w") as output:
			for insert_data in inserts:
				output.write(json.dumps(insert_data) + "\n")
				self.cursor.execute(insert_coord_query.format(
					address=insert_data["address"],
					latitude=insert_data["latitude"],
					longitude=insert_data["longitude"]
				))
				self.connection.commit()

		self.connection.close()

	def output(self):
		job_output = self.config_parser.get("jobs", "GeocodeTaskOutput")
		output = self.create_output_path(job_output)
		return luigi.LocalTarget(output)