.PHONY: check

test:
	pytest --cov-report=xml

test-update:
	pytest --snapshot-update

lint: ## Run ruff linter and type checker
	@uv run ruff check --fix
	@uv run ruff format
	@uv run ty check .

pre-commit-install: ## Install pre-commit hooks
	@uv run pre-commit install

pre-commit: ## Run pre-commit hooks
	@uv run pre-commit run --all-files

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
