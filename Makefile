.PHONY: check

test:
	pytest --cov=great_tables --cov-report=xml

test-update:
	pytest --snapshot-update

	