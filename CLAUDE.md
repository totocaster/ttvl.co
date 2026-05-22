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
- **Obsidian Hub**: `/content/obsidian.md` → `/obsidian/`, collecting Obsidian plugins, vault tools, life-metrics tooling, and AI-agent context workflows

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
- Text Fragments API (native browser support only)
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

### Obsidian Projects
- `/content/obsidian.md` is the hub page for Obsidian-related work: plugins, vault search/discovery tools, plain-text metric workflows, and agent-facing vault tooling.
- Projects associated primarily with Obsidian should use `project.category: /obsidian` in frontmatter so the Projects grid shows the `obsidian` scope under the project name.
- When adding a new Obsidian plugin or related vault/agent tool to projects, update `/content/obsidian.md` in the same change so the hub stays current.
- Obsidian-related project pages may still live under `/content/project-humane/` when that matches the existing URL structure or aliases; the `project.category` controls the visible scope label.

### Monthly Logs
- Filename format: `YYYY.MM.md`
- Custom permalink creates year/month URL structure
- Include summary in frontmatter for index pages

#### Generating Monthly Log Summaries
When user provides journal entries for summarization:

1. **Accept the journal text** from the user (they'll paste it or provide a file)
2. **Generate summary** using this prompt:
   > Act as somebody who summarizes journal entries into publicly shareable bullet points of things created, made, or done. Generate bullet points of major events and projects from first person perspective. Everything that could be of interest to others about what was produced or made should be mentioned. Omit overly personal details. Reference previous months if relevant but keep self-contained. Output in Markdown with single-level lists only (no sublists).

3. **Create the log file**:
   - Filename: `/content/log/YYYY-MM.md` (e.g., `2025-01.md`)
   - Frontmatter:
     ```yaml
     ---
     title: 'YYYY.MM'
     date: YYYY-MM-DD  # Last day of month
     ---
     ```
   - Add generated bullet points
   - Leave space for manual prose summary

4. **Format considerations**:
   - Use `-` for bullets (not `*`)
   - Link to published work: `[Title](/path/)`
   - Italicize emphasis: `_term_`
   - Bold names: `**Person Name**`

### Image Optimization
- Photography: Keep high quality for technical documentation
- General content: Optimize for web (max 2000px wide)
- Store in `/static/images/` with descriptive names

### Text Fragments API
Native browser feature for deep-linking to specific text:
- Auto-updates URL when text is selected (5-500 characters)
- Clears URL when text is deselected
- Keyboard shortcuts: Cmd/Ctrl+Shift+L to update URL, Escape to clear
- Native support only (Chrome 89+, Edge 89+, Firefox 131+, Safari 18.2+)
- No polyfills or fallbacks - silently disabled on unsupported browsers

## Deployment

Auto-deploys from main branch via DigitalOcean App Platform. Configuration in `.do/app.yaml`.

GitHub Actions runs Claude Code Review on PRs (`.github/workflows/claude-review.yml`).

## Important Conventions

1. **No NPM/Node**: Pure Hugo build, no package.json
2. **Content-First**: All content in Markdown with YAML frontmatter
3. **SEO**: Use descriptive titles and summaries in frontmatter
4. **Performance**: Minimize external resources, optimize images
5. **Accessibility**: Maintain semantic HTML, support high contrast mode
6. **Native-Only Features**: Browser-native APIs without polyfills (e.g., Text Fragments)

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
