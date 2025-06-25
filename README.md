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

## License

All rights reserved. The content and code in this repository are not available for reuse without explicit permission.

---

Last updated: June 25, 2025
