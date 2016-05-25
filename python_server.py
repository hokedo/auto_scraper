#!/usr/bin/env python
import web
import sys
import json
import traceback
from scripts.utils import get_parameters
from scripts.utils import create_files
from scripts.utils import requestPage
urls = ('/', 'server')
#render = web.template.render('templates/')

app = web.application(urls, globals())

#my_form = web.form.Form(web.form.Textbox('', class_='textfield', id='textfield'),)

class server:
	def GET(self):
		callback_name = web.input(callback='callback').callback
		web.header('Content-Type', 'application/javascript')
		try:
			request_url = web.ctx.env.get("REQUEST_URI")
			parameters = get_parameters(request_url)
			if "page_url" in parameters:
				html = requestPage(parameters["page_url"])
				content = json.dumps({"html" : html})
			else:
				create_files(parameters)
				content = "'Succesfully generated crawler'"
		except Exception as e:
			content = "\"Error at generating crawler: {}\"".format(e)
			sys.stderr.write(str(traceback.format_exc()))

		return "{callback_name}({content})".format(callback_name=callback_name,
													content=content)


if __name__ == '__main__':
    app.run()
