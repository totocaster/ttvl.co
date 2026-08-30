# ttvl.co

Source for [ttvl.co](https://ttvl.co/), Toto Tvalavadze's public notebook and project archive. The site covers analog photography, bookbinding, notebook systems, humane interfaces, Obsidian tools, essays, visual records, and a monthly work log.

## Stack

- [Hugo Extended](https://gohugo.io/) renders the site and compiles its SCSS. DigitalOcean is pinned to Hugo `0.164.0` Extended in `.do/app.yaml`.
- Hugo Pipes minifies and fingerprints the main stylesheet and most JavaScript assets. There is no Node, npm, package manifest, theme, or separate frontend build command.
- The site's own browser code is vanilla JavaScript. Optional third-party browser code is limited to a vendored `model-viewer` `4.3.1` build on pages with 3D models, Campaign Monitor's hosted subscription-form helper, and Memberful's hosted membership embed.
- DigitalOcean App Platform builds and hosts the static output from `main`; Cloudflare sits in front of the site.

## Repository map

```text
.
├── assets/
│   ├── js/                 # Search, note filters, lightbox, text fragments, pronunciation
│   └── scss/               # Main, membership, and component styles
├── content/                # Markdown content and section indexes
│   ├── bookbinding/
│   ├── darkroom/
│   ├── flaneur/            # Numbered newsletter dispatches
│   ├── leaves/             # Loose Leaves section index; images live in static/leaves
│   ├── log/                # Monthly YYYY-MM.md entries
│   ├── newsletter/         # Newsletter landing page and archive
│   ├── notebook-system/
│   ├── notes/
│   ├── obsidian/
│   ├── project-humane/
│   ├── projects/           # Generated project archive landing page
│   └── traces/
├── layouts/
│   ├── _default/           # Base, list, single, RSS, A-Z, and utility layouts
│   ├── partials/           # Shared page and card components
│   ├── shortcodes/         # Content-facing components
│   └── <section>/          # Section-specific layouts
├── static/
│   ├── downloads/          # PDFs and printable/3D files
│   ├── flaneur/            # Newsletter images
│   ├── leaves/             # Date-prefixed Loose Leaves scans
│   ├── traces/             # Downloadable trace assets such as GLB models
│   ├── ui/                 # Logos and interface images
│   ├── vendor/             # Vendored third-party browser code and licenses
│   ├── visuals/            # Content images and project thumbnails
│   └── llms.txt            # Concise machine-readable site guide
├── tools/
│   ├── build-production.sh # Clean production build and version calculation
│   └── email_templates/    # Campaign Monitor membership email template
├── .do/app.yaml            # DigitalOcean App Platform definition
├── hugo.toml               # Hugo, output, subscription, and version configuration
├── CLAUDE.md               # Coding-agent guidance (AGENTS.md is a symlink to it)
└── public/                 # Generated, ignored output
```

## Development and builds

Install Hugo Extended. To match production exactly, use the version in `.do/app.yaml`.

```bash
# Include draft content while editing
hugo server -D

# Preview published content only
hugo server

# Build the same way DigitalOcean does
sh ./tools/build-production.sh

# Build directly without cleaning public/
HUGO_SITE_UPDATE=$(git rev-list --count HEAD) hugo --destination ./public
```

`tools/build-production.sh` obtains full Git history when necessary, derives `HUGO_SITE_UPDATE` from the repository's commit count, removes `public/`, and runs Hugo. The generated directory is intentionally ignored by Git.

## Content and URLs

| Source | Canonical output | Notes |
| --- | --- | --- |
| `content/bookbinding/` | `/bookbinding/…/` | Bindery tools and practice notes. |
| `content/darkroom/` | `/darkroom/…/` | Analog photography processes, downloads, and equipment projects. |
| `content/flaneur/NNN.md` | `/flaneur/NNN/` and `/flaneur/NNN/email.html` | Each dispatch opts into `HTML` and `email` outputs in frontmatter. |
| `content/newsletter/_index.md` | `/newsletter/` | Subscription page and archive assembled from Flaneur dispatches. |
| `content/leaves/_index.md` | `/leaves/` | The layout reads `static/leaves/YYYY-MM-DD-description.jpeg`; there is no Markdown file per leaf. |
| `content/log/YYYY-MM.md` | `/log/YYYY/MM/` | The URL comes from the page date and the permalink rule in `hugo.toml`. |
| `content/notebook-system/_index.md` | `/project-humane/notebook-system/` | The section index has a canonical override; its child guides remain under `/notebook-system/`. |
| `content/notes/` | `/notes/…/` | The old `/writings/` and `/essays/` paths are aliases. |
| `content/obsidian/` | `/obsidian/…/` | Plugins, vault tools, and related plain-text workflows. |
| `content/project-humane/` | `/project-humane/…/` | Humane-interface and command-line projects. |
| `content/projects/_index.md` | `/projects/` | Discovers pages anywhere on the site with `project` frontmatter. |
| `content/traces/` | `/traces/…/` | Scans, photographs, documents, and interactive spatial records. |

Top-level Markdown files provide the home page and standalone pages such as About, Colophon, AI transparency, A-Z, Links, and Membership. Prefer canonical paths in internal links and retain existing aliases only for compatibility.

## Frontmatter conventions

Project cards are driven by a nested object rather than by content location:

```yaml
date: 2026-07-13
description: "Page summary used by metadata and cards"
featured: true # optional; exposes the page on the home page
project:
  year: 2026 # or: ongoing
  category: /obsidian
  description: "Short project-grid description"
  image: /visuals/project-thumbs/example.png
```

The Projects archive includes every page or section with `project` metadata, groups the special `ongoing` value first, and then groups dated projects by year.

Notes use `category: collected`, `category: thinking`, or `category: longform`; missing categories render as `thinking`. The Notes index filters these categories in the browser and preserves the chosen category in the query string. Note pages also calculate backlinks from canonical internal links during the Hugo build.

Feature-specific scripts are opt-in where practical:

- Set `lightbox: true` on a page that uses `photo-gallery`.
- Set `model_viewer: true` on a page that uses `model-viewer`.
- Set `pronunciation_audio` on a page that uses `pronunciation-name`.

## Shortcodes

| Shortcode | Purpose |
| --- | --- |
| `resources` | Renders a Markdown link list as a manifest of downloads (with build-time sizes) and external sources. |
| `flaneur-gallery` | Two-column dispatch gallery that also renders in the email layout. |
| `membership-link` | Links its inner Markdown to `params.membershipURL`. |
| `model-viewer` | Accessible interactive GLB viewer with poster and no-JavaScript fallback; requires `src`, `poster`, and `alt`. |
| `photo-gallery` | Lazy-loaded linked-image gallery prepared for the lightbox. |
| `project-grid` | Renders an explicitly ordered comma-separated list of project pages. |
| `pronunciation-name` | Audio pronunciation control, currently used on the About page. |
| `toc` | Renders Hugo's table of contents for the current page. |
| `youtube` | Lazy-loaded responsive YouTube iframe. |

## Generated features

- **Search:** On layouts using the shared head, `?` opens an accessible overlay. The JSON index is fetched on first use, results are limited to ten, and arrow keys, Enter, Escape, and focus trapping are supported. `layouts/index.json` currently indexes regular content whose Hugo type is neither `page` nor `json`, so standalone utility pages are not included.
- **Text fragments:** On shared-head layouts and browsers that expose the native Text Fragments API, selecting 6–499 characters updates the URL. `Cmd/Ctrl+Shift+L` refreshes the fragment for the selection and Escape clears it. There is no polyfill.
- **Notes:** Category filtering uses `?category=…`; note backlinks are generated at build time.
- **Images:** Loose Leaves and pages using `photo-gallery` can opt into a keyboard-accessible lightbox.
- **3D records:** Pages with `model_viewer: true` load the vendored `model-viewer` module only on that page.
- **Appearance:** The site follows `prefers-color-scheme` for dark mode and includes selected `prefers-contrast: more` rules. There is no theme toggle or mobile-menu script; the compact navigation scrolls horizontally.
- **Feeds and indexes:** Hugo generates `/index.xml`, `/index.json`, `/sitemap.xml`, and `/robots.txt`. The custom RSS template includes Log, Darkroom, Bookbinding, Notes, Flaneur, Project Humane, and Obsidian entries.

## Newsletter workflow

1. Copy the most recent numbered issue to the next zero-padded filename, for example `content/flaneur/015.md`.
2. Update its title, description, publication date, and `outputs: ["HTML", "email"]` frontmatter.
3. Store issue-specific images in `static/flaneur/` and reference them from Markdown.
4. Use `flaneur-gallery` when a dispatch needs a responsive image pair or grid.
5. Verify both `/flaneur/015/` and `/flaneur/015/email.html`; test the latter in Campaign Monitor because email-client CSS and URL handling differ from browsers.

The separate `tools/email_templates/insider_template.html` file is for the membership/ROAM Campaign Monitor template, not for Flaneur dispatch rendering.

## Site versioning and deployment

The footer displays `vMAJOR.MINOR.UPDATE`:

- `major` and `minor` come from `[params.version]` in `hugo.toml` and currently identify the `v7.7` site structure. `MAJOR` identifies the site era; `MINOR` advances for visible structural or publishing-system revisions rather than routine content posts.
- Production sets `UPDATE` to the Git commit count through `HUGO_SITE_UPDATE`.
- `params.version.update` is a local fallback for direct Hugo commands that do not set the environment variable.

DigitalOcean watches `main`, uses the Hugo buildpack with Extended enabled, and runs `sh ./tools/build-production.sh`. There is currently no repository-hosted CI or automated test suite.

## Verification

For content-only changes, run a published build. For template, SCSS, JavaScript, or responsive-layout changes:

1. Run `hugo server -D` and inspect the affected pages.
2. Exercise search, keyboard focus, system dark mode, and responsive breakpoints when relevant.
3. Verify output-specific pages such as newsletter email HTML, the JSON search index, RSS, redirects, and aliases when changed.
4. Run `sh ./tools/build-production.sh` before deployment and investigate any new warnings.

## License

Source code is licensed under the [MIT License](LICENSE). Text, photographs, images, PDFs, and other content are not licensed for reuse; see [LICENSE-CONTENT](LICENSE-CONTENT). Third-party assets retain their own licenses, including the license stored beside the vendored `model-viewer` build.
