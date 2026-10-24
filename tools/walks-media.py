# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3"]
# ///
"""Publish the walks' photographs to DigitalOcean Spaces.

    uv run tools/walks-media.py            # upload the photographs not yet there
    uv run tools/walks-media.py --check    # list them without uploading

The rendered photographs and thumbnails stay private in .local/walks/media
(tools/walks-photos.py makes them). The site reads them from the shared Space
ttvl-websites (fra1), under ttvl.co/traces/walks/ on its CDN, each named with
a hash of its contents (2022-10-01-s0399-01.c99e1edf2c.jpg), the way toto.photo
stores its books: a changed picture is a new address, so every file is cached
for a year as immutable. The names come from tools/build-walks.py, which
writes the same addresses into data/walks.json. Files already in the Space are
skipped; nothing is ever deleted from it.

The key is a Spaces key scoped to ttvl-websites, read from the macOS Keychain
(service ttvl-websites-spaces) or from SPACES_KEY and SPACES_SECRET.
docs/walks.md.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import boto3
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
BUCKET, REGION = "ttvl-websites", "fra1"
spec = importlib.util.spec_from_file_location("walks", Path(__file__).with_name("build-walks.py"))
walks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(walks)
PREFIX = walks.MEDIA_URL.split(".digitaloceanspaces.com/", 1)[1]  # ttvl.co/traces/walks/


def credentials():
    if os.environ.get("SPACES_KEY") and os.environ.get("SPACES_SECRET"):
        return os.environ["SPACES_KEY"], os.environ["SPACES_SECRET"]
    found = subprocess.run(["security", "find-generic-password", "-s", "ttvl-websites-spaces"], capture_output=True, text=True)
    account = next((line.split('"')[3] for line in found.stdout.splitlines() if '"acct"' in line), None)
    secret = subprocess.run(["security", "find-generic-password", "-s", "ttvl-websites-spaces", "-w"], capture_output=True, text=True).stdout.strip()
    if not account or not secret:
        sys.exit("No Spaces key: add one to the Keychain as ttvl-websites-spaces, or set SPACES_KEY and SPACES_SECRET.")
    return account, secret


def wanted():
    """Every photograph and thumbnail the walks show, from the private record."""
    records = json.loads((ROOT / ".local/walks/photos.json").read_text())["records"]
    names = {Path(image[field]).name for record in records for image in record["images"] for field in ("src", "thumb")}
    missing = sorted(name for name in names if not (walks.MEDIA / name).is_file())
    if missing:
        sys.exit(f"Missing rendered photographs in .local/walks/media: {', '.join(missing[:5])}")
    return sorted(walks.MEDIA / name for name in names)


def publish(paths, check=False, log=print):
    """Upload the files the Space lacks; return how many were uploaded."""
    key, secret = credentials()
    space = boto3.client("s3", region_name=REGION, endpoint_url=f"https://{REGION}.digitaloceanspaces.com",
                         aws_access_key_id=key, aws_secret_access_key=secret)
    have = set()
    for page in space.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=PREFIX):
        have.update(item["Key"] for item in page.get("Contents", []))
    todo = [p for p in paths if PREFIX + walks.media_name(p) not in have]
    for n, path in enumerate(todo, 1):
        name = walks.media_name(path)
        if check:
            log(f"would upload {name}")
            continue
        body = path.read_bytes()
        space.put_object(Bucket=BUCKET, Key=PREFIX + name, Body=body, ACL="public-read", ContentType="image/jpeg",
                         CacheControl="public, max-age=31536000, immutable", Metadata={"sha256": hashlib.sha256(body).hexdigest()})
        if n % 50 == 0 or n == len(todo):
            log(f"uploaded {n} of {len(todo)}")
    log(f"{len(paths) - len(todo)} already in the Space, {len(todo)} {'to upload' if check else 'uploaded'}")
    return len(todo)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="list what would be uploaded")
    args = parser.parse_args()
    try:
        publish(wanted(), check=args.check)
    except ClientError as error:
        sys.exit(f"Spaces said: {error}")


if __name__ == "__main__":
    main()
