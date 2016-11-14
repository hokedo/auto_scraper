#!/usr/bin/env python

import sys
import json

if __name__ == "__main__":
		hotel_properties = {
			"name": "HOTEL_NAME",
			"address": "HOTEL_ADDRESS"
		} 
		review_properties = {
			"text": "REVIEW_TEXT",
			"author": "REVIEW_AUTHOR",
			"original_date": "REVIEW_DATE",
			"original_score": "REVIEW_SCORE",
			"title": "REVIEW_TITLE"
		}
		
		for line in sys.stdin:
			try:
				data = json.loads(line.strip())
			except:
				continue
			for prop in hotel_properties:
				if prop in data and data[prop]:
					print "{}\t{}".format(data[prop].encode("utf-8"), hotel_properties[prop])
			for prop in review_properties:
				for review in data.get("review_list", []):
					if prop in review and review[prop].strip():
						text = review[prop].encode("utf-8").strip()
						if "\n" in text:
							for chunk  in text.split("\n"):
								print "{}\t{}".format(chunk, review_properties[prop])
						elif "\t" in text:
							for chunk  in text.split("\t"):
								print "{}\t{}".format(chunk, review_properties[prop])
						else:		
							print "{}\t{}".format(text, review_properties[prop])
