HTMLCOV="htmlcov/"

tox: clean
	tox

test: clean
	nosetests -v --no-byte-compile --with-coverage --cover-package=simiki --cover-erase -s

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
