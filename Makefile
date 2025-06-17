.PHONY: check

test:
	pytest --cov=great_tables --cov-report=xml --cov-report=term-missing

test-update:
	pytest --snapshot-update

