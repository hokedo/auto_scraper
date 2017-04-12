import re
import json
import luigi
import requests

from auto_scraper.base_psql_task import BasePsqlTask

class PopulatePOITask(BasePsqlTask):
	def run(self):
		output_file_path = self.output().path
		api_key = self.config_parser.get("api_keys", "places_api")
		api_url = self.config_parser.get("jobs", "GooglePlacesApi")
		insert_poi_query_path = self.config_parser.get("jobs", "InsertPOISqlTemplate")

		with open(insert_poi_query_path) as insert_poi_query_file:
			insert_poi_query = insert_poi_query_file.read().strip()

		# TODO: remove hardcoding
		interesting_cities = ["Cluj"]
		# TODO: remove hardcoding
		interesting_types = ["school"]
		inserts = []

		for city in interesting_cities:
			for type in interesting_types:
				url = api_url.format(
					key=api_key,
					city=city,
					type=type
				)
				inserts += self.get_poi_data(url, type)

		self.get_connection()
		with open(output_file_path, "w") as output:
			for insert_data in inserts:
				output.write(json.dumps(insert_data) + "\n")
				query = insert_poi_query.format(
					name=insert_data["name"],
					address=insert_data["address"],
					rating=insert_data["rating"],
					type=insert_data["type"],
					latitude=insert_data["latitude"],
					longitude=insert_data["longitude"],
				)
				self.cursor.execute(query)
				self.connection.commit()

		self.cursor.close()
		self.connection.close()

	def output(self):
		job_output = self.config_parser.get("jobs", "PopulatePOITaskOutput")
		output = self.create_output_path(job_output)
		return luigi.LocalTarget(output)

	def get_poi_data(self, start_url, type):
		results = []
		url =  start_url
		while url:
			self.logger.info("Requesting:\t%s", url)
			response = requests.get(url)
			data = json.loads(response.text)
			for result in data.get("results", []):
				results.append({
					"name": result["name"],
					"address": result["formatted_address"],
					"rating": result["rating"],
					"type": type,
					"latitude": result["geometry"]["location"]["lat"],
					"longitude": result["geometry"]["location"]["lng"],
				})
			if result.get("next_page_token"):
				url = re.sub(r"&pagetoken=.*", "&pagetoken="+result["next_page_token"], url)
			else:
				url = None
		return results