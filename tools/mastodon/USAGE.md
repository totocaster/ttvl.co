# Mastodon Hugo

A Go CLI tool that fetches Mastodon posts from a specific user and generates Hugo-compatible Markdown files with downloaded media attachments.

> [!IMPORTANT]  
> This tool is primarily designed to work on my website, [ttvl.co](https://ttvl.co), and is not widely supported as a generic tool. Pull requests are welcome, but there is no plan to make it a universal, almighty tool that can do everything.

## Features

- Fetches public posts from any Mastodon instance
- Downloads all attached images and videos
- Generates Hugo-compatible Markdown files with YAML front matter
- Configurable output directories
- Fetch all posts up to a specific status ID (useful for incremental updates)
- Option to ignore replies to other people
- Skip existing posts for fast incremental updates
- Filter posts by trailing tags (case insensitive)
- Simple CLI interface

## Setup

### 1. Get a Mastodon Access Token

1. Go to your Mastodon instance (e.g., https://mastodon.social)
2. Navigate to **Preferences** → **Development** 
3. Click **New Application**
4. Fill in the form:
   - **Application name**: `mastodon-hugo` (or any name you prefer)
   - **Application website**: Leave blank or add your website
   - **Scopes**: Make sure `read` is checked (you can uncheck `write` and `follow`)
5. Click **Submit**
6. Click on your newly created application
7. Copy the **Access token** (not the client key/secret)

### 2. Set Environment Variable

```bash
export MASTODON_TOKEN="your_access_token_here"
```

You can add this to your shell profile (`.bashrc`, `.zshrc`, etc.) to make it permanent.

## Building

```bash
# Build the binary
make build

# Or install to $GOPATH/bin
make install
```

## Usage

### Basic Usage

```bash
# Specify required user parameter
./mastodon-hugo --user your_username
```

### Fetch All Posts

```bash
# Fetch all public posts from a user (ignoring replies to others, but keeping your threads)
./mastodon-hugo --user your_username --ignore-replies
```

### Fetch Posts Up to a Specific Status

```bash
# Fetch all posts up to a specific status ID (useful for incremental updates)
./mastodon-hugo --user your_username --max-status-id 123456789
```

### Incremental Updates (Skip Existing Posts)

```bash
# Only process new posts, skip ones that already exist as markdown files
./mastodon-hugo --user your_username --skip-existing
```

### Filter by Trailing Tags

```bash
# Only process posts that end with a specific tag (case insensitive)
./mastodon-hugo --user your_username --trailing-tag "#BLOG"

# Or use caret notation
./mastodon-hugo --user your_username --trailing-tag "^PUBLISH"

# Tags are stripped from the final markdown output
```

### Custom Parameters

```bash
./mastodon-hugo \
  --instance mastodon.social \
  --user your_username \
  --content-dir ./content \
  --media-dir ./content/attachments \
  --max-status-id 123456789 \
  --ignore-replies \
  --skip-existing \
  --trailing-tag "#BLOG"
```

### CLI Options

- `--instance` - Mastodon instance (default: `mastodon.social`)
- `--user` - Username to fetch posts from (required)
- `--content-dir` - Directory for markdown files (default: `./content`)
- `--media-dir` - Directory for media files (default: `./content/attachments`)
- `--max-status-id` - Fetch all posts up to this status ID (optional)
- `--ignore-replies` - Skip replies to other people, but keep your own threads (optional)
- `--skip-existing` - Skip posts that already exist as markdown files (optional)
- `--trailing-tag` - Only process posts ending with this specific tag, case insensitive (optional)

## Output Format

### File Structure

```
content/
├── 2024-01-15-123456789.md
├── 2024-01-14-123456788.md
└── attachments/
    ├── image1.jpg
    ├── video1.mp4
    └── image2.png
```

### Markdown File Format

Each post becomes a markdown file with YAML front matter:

```yaml
---
date: 2024-01-15T10:30:00Z
original_url: https://mastodon.social/@username/123456789
media:
  - image1.jpg
  - video1.mp4
---

This is the post content with HTML tags stripped
and line breaks preserved from the original post.
```

## Integration with Hugo

### In Your Hugo Makefile

```makefile
# Add this to your Hugo project's Makefile
fetch-mastodon:
	cd path/to/mastodon-hugo && ./mastodon-hugo --content-dir ../hugo-site/content/posts

build: fetch-mastodon
	hugo
```

### Example Hugo Template

You can access the media files in your Hugo templates:

```html
{{ if .Params.media }}
<div class="post-media">
  {{ range .Params.media }}
    {{ if or (strings.HasSuffix . ".jpg") (strings.HasSuffix . ".png") (strings.HasSuffix . ".gif") }}
      <img src="/attachments/{{ . }}" alt="Mastodon media" />
    {{ else }}
      <video controls src="/attachments/{{ . }}"></video>
    {{ end }}
  {{ end }}
</div>
{{ end }}

<!-- Link back to original Mastodon post -->
{{ if .Params.original_url }}
<p><a href="{{ .Params.original_url }}" target="_blank">View original post on Mastodon</a></p>
{{ end }}
```

## Development

```bash
# Download dependencies
make deps

# Build
make build

# Clean
make clean

# Help
make help
```

## Requirements

- Go 1.21 or later
- Internet connection for fetching posts and media
- Valid Mastodon access token

## Notes

- Only fetches **public** posts
- Skips reblogs/boosts (fetches original content only)
- Media files are downloaded as-is (no processing/resizing)
- Existing files are not re-downloaded (basic deduplication)
- HTML tags are stripped from post content while preserving line breaks
- Post content is stored in markdown body, not in YAML front matter
- When using `--max-status-id`, the tool fetches ALL posts chronologically up to that status ID (useful for incremental syncing)
- The `--ignore-replies` flag skips posts that are replies to other users' posts, but keeps your own threads (replies to your own posts)
- The `--skip-existing` flag checks for existing markdown files and skips processing them, making subsequent runs much faster
- The `--trailing-tag` flag filters posts by their ending tag (case insensitive) and removes the tag from the final markdown output 