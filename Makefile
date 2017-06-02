HTMLCOV="htmlcov/"

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  tox        to run test by tox"
	@echo "  test       to run test by nosetests with coverage"
	@echo "  covhtml    to run test by nosetests and create html report"
	@echo "  clean      to clean temporary files without .tox"
	@echo "  cleanall   to clean temporary files with .tox"

tox: clean
	tox

test: clean
	nosetests -v --no-byte-compile --with-coverage --cover-package=simiki --cover-erase -s
	flake8 --version
	flake8 simiki/ tests/

covhtml: clean
	# coverage run setup.py nosetests
	nosetests    # arguments already configured in setup.cfg
	coverage html
	cd ${HTMLCOV} && python -m SimpleHTTPServer

cleanall: clean
	rm -rf .tox

clean:
	coverage erase
	python setup.py clean
	find simiki/ -name '*.pyc' -delete
	find tests/ -name '*.pyc' -delete
	rm -rf htmlcov
	rm -rf build dist simiki.egg-info
