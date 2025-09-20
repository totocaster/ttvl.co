# Agentic AI Instructions

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal website built with Hugo static site generator. Focus on analog photography, notebook systems, and creative writing. No external JavaScript dependencies, pure Hugo build.

## Essential Commands

```bash
# Development
hugo server -D              # Start dev server with drafts
hugo server                 # Start dev server (published only)

# Build
hugo --destination ./public # Production build
rm -r ./public && hugo      # Clean build

# Content Management
hugo new darkroom/title.md  # Create photography article
hugo new flaneur/title.md   # Create newsletter issue
hugo new log/YYYY.MM.md    # Create monthly log
```

## Architecture

### Content Types & Permalinks
- **Monthly Logs**: `/content/log/YYYY.MM.md` → `/log/YYYY/MM/`
- **Newsletter**: `/content/flaneur/*.md` → Dual output (HTML + email format)
- **Photography**: `/content/darkroom/*.md` → Technical documentation
- **Visual Journal**: `/content/leaves/*.md` → Scanned loose leaves from Unbound Notebook System

### Key Configuration
- Main config: `hugo.toml`
- Custom output formats for newsletter (HTML + email)
- Memberful subscription IDs: Monthly (121779), Yearly (121780)

### Template Structure
- Layouts follow Hugo's lookup order
- Custom shortcodes in `/layouts/shortcodes/`:
  - `flaneur-gallery`: Responsive galleries
  - `download-section`: Download boxes
  - `toc`: Table of contents
  - `youtube`: Video embeds
  - `membership-link`: Memberful integration

### Styling Architecture
SCSS files in `/assets/scss/`:
- Component-based architecture
- Variables in `_variables.scss`
- Dark mode support built-in
- Mobile-first responsive design

### JavaScript Features
Vanilla JS in `/assets/js/`:
- Site search (activated with `?` key)
- Lightbox for images
- Mobile menu toggle
- No build step required

## Development Patterns

### Creating Newsletter Issues
1. Create file: `hugo new flaneur/YYYY.MM.md`
2. Email version auto-generates at `/flaneur/YYYY.MM/email/`
3. Use `flaneur-gallery` shortcode for image galleries

### Adding Photography Content
1. Create file in `/content/darkroom/`
2. Include technical metadata in frontmatter
3. Optimize images before adding to `/static/images/`

### Monthly Logs
- Filename format: `YYYY.MM.md`
- Custom permalink creates year/month URL structure
- Include summary in frontmatter for index pages

### Image Optimization
- Photography: Keep high quality for technical documentation
- General content: Optimize for web (max 2000px wide)
- Store in `/static/images/` with descriptive names

## Deployment

Auto-deploys from main branch via DigitalOcean App Platform. Configuration in `.do/app.yaml`.

GitHub Actions runs Claude Code Review on PRs (`.github/workflows/claude-review.yml`).

## Important Conventions

1. **No NPM/Node**: Pure Hugo build, no package.json
2. **Content-First**: All content in Markdown with YAML frontmatter
3. **SEO**: Use descriptive titles and summaries in frontmatter
4. **Performance**: Minimize external resources, optimize images
5. **Accessibility**: Maintain semantic HTML, support high contrast mode

## Special Files

- `/static/llms.txt`: AI-friendly site description
- `/static/robots.txt`: Search engine directives
- `/data/`: Hugo data files for structured content

## Testing

No automated tests. Manual verification:
1. Run `hugo server -D` and check localhost:1313
2. Verify responsive design at multiple breakpoints
3. Test search functionality with `?` key
4. Check dark mode toggle
5. Validate HTML output in `/public/` after build