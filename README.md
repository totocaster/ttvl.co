# ttvl.co

Personal website of Toto Tvalavadze, built with [Hugo](https://gohugo.io/). A digital garden and documentation hub for various personal and creative projects, with a strong focus on analog photography, notebook systems, and thoughtful writing.

## Overview

This is the source code for [ttvl.co](https://ttvl.co/), featuring:

- **Darkroom & Photography**: Technical documentation and guides for analog photography
- **Unbound Notebook System (UNS)**: Framework for hybrid digital/analog note-taking
- **Flaneur Newsletter**: Monthly newsletter archive with email-friendly output
- **Project Humane**: Personal productivity tools and projects
- **Writings & Essays**: Long-form articles and thoughts
- **Monthly Logs**: Personal journal entries from December 2021 onwards
- **Visual Journal (Leaves)**: Photography and visual notes

## Technology Stack

- **Static Site Generator**: Hugo v0.139.0 Extended
- **Styling**: SCSS (compiled by Hugo's built-in processor)
- **JavaScript**: Vanilla JS (no external dependencies)
- **Deployment**: DigitalOcean App Platform
- **Content**: Markdown files
- **Membership**: Memberful integration for paid subscriptions

## Project Structure

```
.
├── assets/               # Frontend assets processed by Hugo
│   ├── js/              # JavaScript files
│   │   ├── lightbox.js  # Simple lightbox for images
│   │   └── menu.js      # Mobile menu functionality
│   └── scss/            # SCSS stylesheets
│       ├── style.scss   # Main styles
│       └── *.scss       # Component styles
├── content/             # All site content in Markdown
│   ├── darkroom/        # Photography documentation (11 articles)
│   ├── flaneur/         # Newsletter archive (11 issues)
│   ├── leaves/          # Visual journal
│   ├── log/             # Monthly logs (2021-12 to 2025-06)
│   ├── notebook-system/ # UNS documentation
│   ├── project-humane/  # Personal projects
│   ├── writings/        # Essays and articles
│   └── *.md            # Single pages (about, colophon, etc.)
├── layouts/             # Hugo templates
│   ├── _default/        # Default templates
│   ├── flaneur/         # Newsletter-specific layouts
│   ├── partials/        # Reusable components
│   └── shortcodes/      # Custom shortcodes
├── static/              # Static assets (served as-is)
│   ├── downloads/       # PDFs and downloadable resources
│   ├── visuals/         # Images organized by section
│   ├── ui/              # UI assets and logos
│   └── llms.txt         # AI/LLM-friendly site description
├── tools/               # Development tools
│   └── email_templates/ # Campaign Monitor newsletter templates
├── .do/                 # DigitalOcean deployment
│   └── app.yaml         # Deployment configuration
├── hugo.toml            # Hugo configuration
└── public/              # Generated site (gitignored)
```

## Configuration

### Hugo Configuration (hugo.toml)
- Base URL: `https://ttvl.co/`
- Language: US English
- Custom permalinks for logs: `/log/:year/:month/`
- Memberful integration with plan IDs:
  - Monthly: 121779
  - Yearly: 121780
- Custom output format for Flaneur emails

### Deployment Configuration (.do/app.yaml)
- Hugo version: 0.139.0 Extended
- Auto-deploy from main branch
- Build command: `rm -r ./public; hugo --destination ./public`

## Development

1. Install [Hugo Extended](https://gohugo.io/installation/) (v0.139.0 or later)
2. Clone this repository
3. Run the development server:
   ```bash
   hugo server -D
   ```
4. Visit `http://localhost:1313`

### Build Commands
- Development: `hugo server -D`
- Production build: `hugo --destination ./public`
- Clean build: `rm -r ./public; hugo --destination ./public`

## Content Management

### Content Sections

- **`/darkroom/`** - Analog photography guides and documentation
- **`/flaneur/`** - Newsletter issues with web and email versions
- **`/leaves/`** - Visual journal entries
- **`/log/`** - Monthly personal logs (permalink: `/log/YYYY/MM/`)
- **`/notebook-system/`** - UNS templates and documentation
- **`/project-humane/`** - Personal project documentation
- **`/writings/`** - Long-form essays and articles

### Special Features

1. **Flaneur Email Output**: Newsletter posts generate both web and email-friendly HTML versions
2. **LLM Support**: `/static/llms.txt` provides AI-friendly site description
3. **Membership Integration**: Paid subscription support via Memberful
4. **No External Dependencies**: Pure Hugo build with no npm/yarn requirements

## Tools and Templates

### Hugo Shortcodes

The site includes several custom Hugo shortcodes for enhanced content formatting:

#### `flaneur-gallery`
Creates a responsive image gallery that displays images side by side (2 columns on desktop, single column on mobile).

**Usage:**
```markdown
{{< flaneur-gallery >}}
![Image 1 alt text](/path/to/image1.jpg)
![Image 2 alt text](/path/to/image2.jpg)
![Image 3 alt text](/path/to/image3.jpg)
{{< /flaneur-gallery >}}
```

**Features:**
- Automatic responsive grid layout (2 columns → 1 column on mobile)
- Maintains readable-width constraints 
- Works in both web and email templates
- Supports any number of images (wraps to new rows after 2 images)
- Email-compatible CSS (no JavaScript required)

**Email Usage:**
For email templates, manually convert the shortcode to HTML:
```html
<div class="flaneur-gallery">
  <img src="https://ttvl.co/path/to/image1.jpg" alt="Image 1 alt text" />
  <img src="https://ttvl.co/path/to/image2.jpg" alt="Image 2 alt text" />
</div>
```

#### `download-section`
Creates a styled download box with download icons and formatting.

**Usage:**
```markdown
{{< download-section >}}
- [Download File 1](/downloads/file1.pdf)
- [Download File 2](/downloads/file2.pdf)
{{< /download-section >}}
```

#### `toc`
Generates a table of contents from page headers.

**Usage:**
```markdown
{{< toc >}}
```

#### `youtube`
Embeds YouTube videos with responsive container.

**Usage:**
```markdown
{{< youtube "VIDEO_ID" >}}
```

#### `membership-link`
Creates styled membership links using site configuration.

**Usage:**
```markdown
{{< membership-link >}}Join Now{{< /membership-link >}}
```

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

### Testing & Quality Assurance

Since this is a Hugo static site without JavaScript dependencies or tests:

1. **Visual Testing**: Preview changes with `hugo server -D`
2. **Build Verification**: Ensure clean builds with `hugo --destination ./public`
3. **Link Checking**: Verify internal links work correctly
4. **Responsive Design**: Test on multiple screen sizes
5. **Email Template Testing**: Test newsletter templates in Campaign Monitor

### Contributing Guidelines

When making changes:

1. **Content**: Add new content to appropriate directories under `/content/`
2. **Styling**: Edit SCSS files in `/assets/scss/`
3. **Templates**: Modify layouts in `/layouts/`
4. **Images**: Add to `/static/visuals/` in appropriate subdirectories
5. **Downloads**: Place PDFs and resources in `/static/downloads/`

### Key Files for AI Agents

- **`hugo.toml`**: Main configuration file
- **`/static/llms.txt`**: AI-friendly site overview
- **`/layouts/`**: Template structure and logic
- **`/assets/scss/style.scss`**: Main stylesheet
- **`.do/app.yaml`**: Deployment configuration

## License

All rights reserved. The content and code in this repository are not available for reuse without explicit permission.

---

Last updated: July 13, 2025
