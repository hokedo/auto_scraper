#!/usr/bin/env python
import re
import web
import sys
import json
import traceback
from scripts.utils import get_parameters
from scripts.utils import create_files
from scripts.utils import requestPage
urls = ('/.*', 'server')
#render = web.template.render('templates/')

app = web.application(urls, globals())

#my_form = web.form.Form(web.form.Textbox('', class_='textfield', id='textfield'),)

class server:
	def GET(self):
		callback_name = web.input(callback='callback').callback
		content = json.dumps({"Error": "Couldn't parse url"})
		try:
			request_url = web.ctx.env.get("REQUEST_URI")
			if request_url == "/":
				web.header('Content-Type', 'text/html')
				html_file = open("./src/html/extractor_generator.html", "r")
				html = html_file.read()
				html_file.close()
				return str(html)

			resource_name = re.search(r"/(.+(\.css|\.js)$)", request_url)
			if resource_name:
				if re.search(".css$", request_url):
					web.header('Content-Type', 'text/css')
					resource_file = open("./src/css/" + resource_name.group(1))
				elif re.search(".js$", request_url):
					web.header('Content-Type', 'application/javascript')
					resource_file = open("./src/js/" + resource_name.group(1))
				
				resource = resource_file.read()
				resource_file.close()
				return str(resource)

			parameters = get_parameters(request_url)
			web.header('Content-Type', 'application/javascript')
			if "page_url" in parameters and len(parameters["page_url"]):
				html = requestPage(parameters["page_url"])
				content = json.dumps({"html" : html})
			if "review_frame" in parameters and len(parameters["review_frame"]):
				create_files(parameters)
				sys.stderr.write(str(parameters))
				content = "'Succesfully generated crawler'"
			if "selector" in parameters:
				content = json.dumps({"type": "OK"})
			
		except Exception as e:
			content = "\"Internal Server Error: {}\"".format(e)
			sys.stderr.write(str(traceback.format_exc()))

		return "{callback_name}({content})".format(callback_name=callback_name,
													content=content)


if __name__ == '__main__':
    app.run()
