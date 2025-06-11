# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Hugo Static Site Development:**
- `make dev` - Start development server with drafts enabled (serves on all interfaces)
- `make build` - Build for production with minification
- `hugo server -D` - Alternative dev server command (local only)

**Synapse Pulse Integration:**
- Set `MASTODON_TOKEN` environment variable before syncing
- `make sync-build` - Sync Mastodon posts and build site
- `make clean` - Remove generated files and synced content

**Manual Mastodon Sync:**
```bash
./tools/mastodon/mastodon-hugo \
  --instance mastodon.social \
  --user ttt \
  --content-dir ./content/synapse-pulse \
  --media-dir ./static/synapse-pulse \
  --max-status-id 113884697682062582 \
  --ignore-replies
```

## Architecture Overview

**Hugo-Based Static Site:**
- Content in `/content/` organized by sections (darkroom, leaves, notebook-system, etc.)
- Templates in `/layouts/` with specialized layouts for different content types
- SCSS styling in `/assets/scss/` using responsive grid system
- Static assets in `/static/`

**Key Layout Structure:**
- Base template uses grid layout: main content + sidebar navigation
- Responsive design with mobile menu toggle
- Dark/light mode support via CSS media queries
- Custom output formats including email templates for newsletters

**Content Sections:**
- `/content/log/` - Monthly development logs with custom permalinks
- `/content/flaneur/` - Newsletter content with email output format
- `/content/synapse-pulse/` - Auto-generated from Mastodon (excluded from main RSS)
- `/content/leaves/` - Personal notes with image grid layout
- `/content/darkroom/` - Photography-related content

**Special Features:**
- Email templates in `/tools/email_templates/` for Campaign Monitor
- Synapse Pulse integration pulls Mastodon posts automatically
- Custom SCSS grid system with breakpoints and dark mode mixins
- Memberful integration for subscription management

**Generated Content:**
- Synapse Pulse content is auto-generated and git-ignored
- Uses `--max-status-id` for incremental sync
- Media files automatically downloaded and embedded