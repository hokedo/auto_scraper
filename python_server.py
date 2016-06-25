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
		try:
			request_url = web.ctx.env.get("REQUEST_URI")
			if request_url == "/":
				web.header('Content-Type', 'text/html')
				html_file = open("extractor_generator.html", "r")
				html = html_file.read()
				html_file.close()
				return str(html)

			resource_name = re.search(r"/(.+(\.css|\.js))", request_url)
			if resource_name:
				resource_file = open(resource_name.group(1))
				resource = resource_file.read()
				if re.search(".css$", request_url):
					web.header('Content-Type', 'text/css')
				elif re.search(".js$", request_url):
					web.header('Content-Type', 'application/javascript')
				
				return str(resource)

			parameters = get_parameters(request_url)
			web.header('Content-Type', 'application/javascript')
			if "page_url" in parameters:
				html = requestPage(parameters["page_url"])
				content = json.dumps({"html" : html})
			else:
				create_files(parameters)
				content = "'Succesfully generated crawler'"
		except Exception as e:
			content = "\"Internal Server Error: {}\"".format(e)
			sys.stderr.write(str(traceback.format_exc()))

		return "{callback_name}({content})".format(callback_name=callback_name,
													content=content)


if __name__ == '__main__':
    app.run()
