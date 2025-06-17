.PHONY: check

test:
	pytest --cov-report=xml

test-update:
	pytest --snapshot-update

