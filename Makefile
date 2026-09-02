# ttvl.co task runner. Hugo Extended and uv are the only tools it expects.
# Run `make` for the list.

.DEFAULT_GOAL := help
.PHONY: help serve serve-drafts build cards cards-check cards-stale cards-all hooks

help: ## Show this list
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-14s %s\n", $$1, $$2}'

serve: ## Hugo dev server with published content only
	hugo server

serve-drafts: ## Hugo dev server including drafts (port 1314)
	hugo server -D --port 1314

build: ## Production-equivalent build into public/
	sh ./tools/build-production.sh

# Social cards live in static/social/ and are committed. Render them locally
# after adding or retitling a note, project page, or hub; the build server
# never renders and only warns when a card is missing.
cards: ## Render the social cards that are missing
	uv run tools/social-cards.py

cards-check: ## List missing, stale, and orphaned social cards (exit 1 if any)
	uv run tools/social-cards.py --check

cards-stale: ## Render missing cards and re-render those whose inputs changed
	uv run tools/social-cards.py --stale

cards-all: ## Re-render every social card (after a design change)
	uv run tools/social-cards.py --all

hooks: ## Install the git pre-commit hook that refuses commits with missing cards
	install -m 755 tools/pre-commit .git/hooks/pre-commit
	@echo "installed .git/hooks/pre-commit"
