# ttvl.co

Personal website of Toto Tvalavadze, built with [Hugo](https://gohugo.io/).

## Overview

This is the source code for [ttvl.co](https://ttvl.co/), a personal website featuring various content sections including:

- Blog posts and articles
- Photography work (darkroom)
- Notebook system templates
- Project documentation
- Personal leaves (notes and thoughts)

## Technology Stack

- **Static Site Generator**: Hugo
- **Styling**: SCSS
- **Deployment**: DigitalOcean App Platform
- **Content**: Markdown files

## Project Structure

```
.
├── assets/          # SCSS and JavaScript files
├── content/         # Markdown content files
├── data/           # Hugo data files
├── layouts/        # Hugo templates
├── static/         # Static assets
├── tools/          # Project tools and templates
│   └── email_templates/  # Email templates for newsletters
└── public/         # Generated site (not tracked in git)
```

## Development

1. Install [Hugo](https://gohugo.io/installation/)
2. Clone this repository
3. Run the development server:
   ```bash
   hugo server -D
   ```
4. Visit `http://localhost:1313`

## Deployment

The site is automatically deployed to DigitalOcean App Platform. Configuration can be found in the `.do/app.yaml` file.

## Content Management

Content is organized in several main sections:

- `/content/darkroom/` - Photography related content
- `/content/leaves/` - Personal notes and thoughts
- `/content/notebook-system/` - Notebook templates and guides
- `/content/project-humane/` - Project documentation

## Tools and Templates

### Email Templates

The project includes email templates for newsletters and member communications:

- `/tools/email_templates/insider_template.html` - Template for ROAM Insider newsletter
  - Used with Campaign Monitor
  - Includes responsive design and inline styles
  - Supports Campaign Monitor's templating system:
    - `<multiline>` tag for main content
    - `<unsubscribe>` tag for unsubscribe links
  - Styled with variable font for ROAM branding
  - Copy-paste ready for Campaign Monitor's template system

## Synapse Pulse Integration

The `/content/synapse-pulse/` section contains automatically generated worklog content from Mastodon posts for the Synapse project.

### Prerequisites

Set your Mastodon access token:
```bash
export MASTODON_TOKEN="your_access_token_here"
```

### Make Commands

- `make build` - Build the website for production
- `make dev` - Build and serve the website for development  
- `make sync-build` - Sync Mastodon posts and build the website
- `make clean` - Clean generated files and Mastodon content

### Manual Sync

```bash
./tools/mastodon/mastodon-hugo \
  --instance mastodon.social \
  --user ttt \
  --content-dir ./content/synapse-pulse \
  --media-dir ./static/synapse-pulse
```

### Implementation Notes

- Generated content is automatically excluded from git
- Posts displayed in reverse chronological order (newest first)
- Media attachments automatically embedded below post content
- Section excluded from main RSS feed and site index
- Uses `original_url` parameter in front matter

## License

All rights reserved. The content and code in this repository are not available for reuse without explicit permission.

---

Last updated: March 30, 2025
