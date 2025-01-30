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

## License

All rights reserved. The content and code in this repository are not available for reuse without explicit permission.

---

Last updated: January 30, 2025
