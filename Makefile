# Makefile for ttvl.co Hugo site

.PHONY: build dev sync-build clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  build       - Build the website for production"
	@echo "  dev         - Build and serve the website for development"
	@echo "  sync-build  - Sync Mastodon posts and build the website"
	@echo "  clean       - Clean generated files and Mastodon content"
	@echo "  help        - Show this help message"

# Build website for production
build:
	@echo "Building website for production..."
	hugo --minify

# Build and serve website for development
dev:
	@echo "Starting development server..."
	hugo server -D --bind 0.0.0.0

# Sync Mastodon posts and build website
sync-build: sync-mastodon build

# Sync Mastodon posts (internal target)
sync-mastodon:
	@echo "Syncing Mastodon posts..."
	@if [ -z "$$MASTODON_TOKEN" ]; then \
		echo "Error: MASTODON_TOKEN environment variable is not set"; \
		echo "Please set your Mastodon access token:"; \
		echo "  export MASTODON_TOKEN='your_access_token_here'"; \
		exit 1; \
	fi
	./tools/mastodon/mastodon-hugo \
		--instance mastodon.social \
		--user ttt \
		--content-dir ./content/synapse-pulse \
		--media-dir ./static/synapse-pulse \
		--max-status-id 113884697682062582 \
		--ignore-replies

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf public/
	rm -rf resources/_gen/
	rm -f content/synapse-pulse/20??-??-??-*.md
	rm -f static/synapse-pulse/*
	@echo "Clean complete" 