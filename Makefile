.PHONY: check

test:
	pytest --cov-report=xml

test-update:
	pytest --snapshot-update

docs-build:
	cd docs \
	  && quartodoc build --verbose \
	  && quarto render

docs-clean:
	cd docs \
	  && rm -rf _site \
	  && rm -rf .quarto \
	  && rm -rf reference \
	  && rm _sidebar.yml
