#!/usr/bin/env sh
set -eu

if shallow="$(git rev-parse --is-shallow-repository 2>/dev/null)" && [ "$shallow" = "true" ]; then
  if ! git fetch --unshallow --quiet 2>/dev/null; then
    echo "Unable to fetch full Git history for the site update count." >&2
    exit 1
  fi
fi

if ! update="$(git rev-list --count HEAD 2>/dev/null)"; then
  echo "Unable to compute HUGO_SITE_UPDATE with git rev-list --count HEAD." >&2
  echo "Confirm the production build command runs from a Git checkout." >&2
  exit 1
fi

case "$update" in
  ''|*[!0-9]*)
    echo "Invalid HUGO_SITE_UPDATE value: $update" >&2
    exit 1
    ;;
esac

export HUGO_SITE_UPDATE="$update"

rm -rf ./public
hugo --destination ./public
