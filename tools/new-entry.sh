#!/bin/sh
# Start a research entry: content/research/<stream>/YYYY-MM-DD-<slug>.md
# with today's date and time, the slug, and an empty title to fill in.
# Usage: make entry STREAM=ambient-computing SLUG=four-corners
set -eu

stream=${1:-}
slug=${2:-}
root="content/research"

streams() {
  for d in "$root"/*/; do
    [ -f "$d/_index.md" ] && printf '  %s\n' "$(basename "$d")"
  done
}

if [ -z "$stream" ] || [ -z "$slug" ]; then
  echo "usage: make entry STREAM=<stream> SLUG=<slug>" >&2
  echo "streams:" >&2
  streams >&2
  exit 2
fi

if [ ! -f "$root/$stream/_index.md" ]; then
  echo "no stream named '$stream'. Streams:" >&2
  streams >&2
  exit 1
fi

case "$slug" in
  *[!a-z0-9-]* | -* | *-)
    echo "SLUG takes lowercase letters, digits, and inner hyphens: '$slug'" >&2
    exit 1
    ;;
esac

file="$root/$stream/$(date +%Y-%m-%d)-$slug.md"
if [ -e "$file" ]; then
  echo "already exists: $file" >&2
  exit 1
fi

# RFC 3339 with a colon in the offset (+0200 -> +02:00).
now=$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\([0-9][0-9]\)$/:\1/')

cat > "$file" <<EOF
---
title: ""
date: $now
slug: $slug
category: progress # finding · progress · question · reading
# answers: question-slug # closes an open question in this stream
---

EOF

echo "$file"
