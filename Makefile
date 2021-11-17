.PHONY: clean compile_translations coverage diff_cover dummy_translations \
        extract_translations fake_translations help pull_translations push_translations \
        quality selfcheck test test-all validate

.DEFAULT_GOAL := help

# PROJECT_ROOT is usually '/edx/src/labxchange-xblocks/' on an Open edX devstack
PROJECT_ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# For opening files in a browser. Use like: $(BROWSER)relative/path/to/file.html
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

clean: ## remove generated byte code, coverage reports, and build artifacts
	find $(PROJECT_ROOT) -name '__pycache__' -exec rm -rf {} +
	find $(PROJECT_ROOT) -name '*.pyc' -exec rm -f {} +
	find $(PROJECT_ROOT) -name '*.pyo' -exec rm -f {} +
	find $(PROJECT_ROOT) -name '*~' -exec rm -f {} +
	cd $(PROJECT_ROOT) && coverage erase
	rm -fr $(PROJECT_ROOT)build/
	rm -fr $(PROJECT_ROOT)dist/
	# Do not delete the .egg-info because it will uninstall the entry point
	# and thus unregister the plugin.
	# rm -fr $(PROJECT_ROOT)*.egg-info

coverage: clean ## generate and view HTML coverage report
	pytest --cov-report html
	$(BROWSER)htmlcov/index.html


quality: ## check coding style with pycodestyle and pylint
	pylint labxchange_xblocks $(PROJECT_ROOT)setup.py
	pylint --py3k labxchange_xblocks $(PROJECT_ROOT)setup.py
	pycodestyle $(PROJECT_ROOT)labxchange_xblocks $(PROJECT_ROOT)setup.py
	isort --check-only --diff --recursive $(PROJECT_ROOT)labxchange_xblocks $(PROJECT_ROOT)setup.py

# test target:
#
# Meant to be run in an `edxapp` virtualenv.  We don't use tox because we need to
# test with the real installation of Open edX and whatever dependencies it
# uses.  We use no-cov and nomigrations because they _really_ speed up the test
# run.
test: clean
	mkdir -p test_root
	python -m pytest -vvv -s --disable-pytest-warnings --ds=lms.envs.test --no-cov --nomigrations $(PROJECT_ROOT)labxchange_xblocks/tests/

diff_cover: test ## find diff lines that need test coverage
	diff-cover coverage.xml

validate: quality test ## run tests and quality checks

selfcheck: ## check that the Makefile is well-formed
	@echo "The Makefile is well-formed."

## Localization targets

extract_translations: ## extract strings to be translated, outputting .mo files
	rm -rf docs/_build
	cd labxchange-xblocks && ../manage.py makemessages -l en -v1 -d django
	cd labxchange-xblocks && ../manage.py makemessages -l en -v1 -d djangojs

compile_translations: ## compile translation files, outputting .po files for each supported language
	cd labxchange-xblocks && ../manage.py compilemessages

detect_changed_source_translations:
	cd labxchange-xblocks && i18n_tool changed

pull_translations: ## pull translations from Transifex
	tx pull -af --mode reviewed

push_translations: ## push source translation files (.po) from Transifex
	tx push -s

dummy_translations: ## generate dummy translation (.po) files
	cd labxchange_xblocks && i18n_tool dummy

build_dummy_translations: extract_translations dummy_translations compile_translations ## generate and compile dummy translation files

validate_translations: build_dummy_translations detect_changed_source_translations ## validate translations
