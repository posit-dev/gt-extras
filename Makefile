.PHONY: check

test:
	pytest --cov-report=xml

test-update:
	pytest --snapshot-update

docs-build:
	cd docs \
	  && quartodoc build --verbose \
	  && quarto render
