deploy: venv tables submodules
		echo "Finished preparing auto_scraper"

submodules:
		git submodule init
		git submodule update --recursive

tables:
		echo "Create a database user with create and grant permissions before executing this script"
		echo "The username should be the same as the current user"
		psql auto_scraper -h localhost -f ./auto_scraper/sql/create_tables.sql
		echo "Make sure to set password to rw_user!"

venv:
		( \
			virtualenv --python=python2.7 venv; \
			. venv/bin/activate; \
			pip install -r requirements.txt; \
			deactivate; \
		)

clean:
		rm -rf venv


#sudo apt-get install build-essential autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7 qt4-dev-tools q$
