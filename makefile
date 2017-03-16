deploy: venv tables submodules
	echo "Finished preparing auto_scraper"

submodules:
	git submodule init
	git submodule update --recursive

tables:
	psql auto_scraper -h localhost -f ./auto_scraper/sql/create_tables.sql

venv:
	( \
		virtualenv venv; \
		. venv/bin/activate; \
		pip install -r requirements.txt; \
		deactivate; \
	)
