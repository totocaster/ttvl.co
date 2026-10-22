# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Render the still of the reply-following instrument: its four phones at
the end of the reply, in light mode on white, at twice their size.

    uv run tools/reply-following-image.py
    uv run tools/reply-following-image.py --at 3.2 --dark --out /tmp/frame.png

The instrument (layouts/shortcodes/reply-following.html) shows this PNG
until its script runs, and feeds get only the PNG; the entry's `image`
makes it the Latest card. The script builds the site with drafts into a
temporary folder, serves it locally, and has a headless Chromium (as
tools/drawing-png.py finds one) photograph the phones and their labels
alone, as the page lays them out at full width. --at shows another moment
and --width another layout, for checking the motion; --dark,
--reduce-motion, and --out go with them.
"""
import argparse
import functools
import http.server
import importlib.util
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
PAGE = "research/hank/streaming-replies/index.html"
STILL = ROOT / "static" / "visuals" / "research" / "hank" / "2026-10-22-reply-following.png"

# The phones and their labels alone, pinned to the corner of the window.
CAPTURE = """<style>
html, body {{ background: {ground} !important; }}
body * {{ visibility: hidden; }}
.reply-following__screens, .reply-following__screens * {{ visibility: visible; }}
.reply-following__screens {{ position: fixed; left: {pad}px; top: {pad}px; width: {width}px; z-index: 9999; overflow: visible; }}
</style>"""
MOMENT = """<script>
addEventListener("load", () => setTimeout(() => {{
  const range = document.querySelector(".reply-following .scrubber input");
  range.value = "{at}";
  range.dispatchEvent(new Event("input"));
}}, 400));
</script>"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def browser():
    spec = importlib.util.spec_from_file_location("drawing_png", ROOT / "tools" / "drawing-png.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.browser()


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--at", type=float, help="the moment in seconds (default: the end)")
    parser.add_argument("--width", type=int, default=1086, help="the phones' row width in px (default 1086, the wide well)")
    parser.add_argument("--dark", action="store_true", help="dark mode")
    parser.add_argument("--reduce-motion", action="store_true", help="prefers reduced motion: no fades, no glide")
    parser.add_argument("--out", type=Path, default=STILL, help=f"the PNG (default {STILL.relative_to(ROOT)})")
    args = parser.parse_args()
    if not shutil.which("hugo"):
        sys.exit("Needs Hugo Extended.")
    chrome = browser()
    pad = 32
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp) / "site"
        port = free_port()
        subprocess.run(
            ["hugo", "--buildDrafts", "--quiet", "--destination", str(site), "--baseURL", f"http://127.0.0.1:{port}/"],
            cwd=ROOT,
            check=True,
        )
        html = (site / PAGE).read_text(encoding="utf-8")
        capture = CAPTURE.format(ground="#000" if args.dark else "#fff", pad=pad, width=args.width)
        html = html.replace("</head>", capture + "</head>", 1)
        if args.at is not None:
            html = html.replace("</body>", MOMENT.format(at=args.at) + "</body>", 1)
        (site / PAGE).with_name("capture.html").write_text(html, encoding="utf-8")

        handler = functools.partial(Quiet, directory=str(site))
        server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            shot = Path(tmp) / "shot.png"
            flags = ["--force-dark-mode", "--blink-settings=preferredColorScheme=0"] if args.dark else []
            if args.reduce_motion:
                flags.append("--force-prefers-reduced-motion")
            subprocess.run(
                [
                    chrome,
                    "--headless",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    "--force-device-scale-factor=2",
                    f"--window-size={args.width + 2 * pad},1400",
                    "--virtual-time-budget=5000",
                    *flags,
                    f"--screenshot={shot}",
                    f"http://127.0.0.1:{port}/{Path(PAGE).parent}/capture.html",
                ],
                check=True,
                capture_output=True,
            )
        finally:
            server.shutdown()
        # Trim to the phones and labels, keeping the margin around them.
        image = Image.open(shot).convert("RGB")
        ground = Image.new("RGB", image.size, (0, 0, 0) if args.dark else (255, 255, 255))
        box = ImageChops.difference(image, ground).getbbox()
        if box:
            m = 2 * pad
            image = image.crop((max(0, box[0] - m), max(0, box[1] - m), min(image.width, box[2] + m), min(image.height, box[3] + m)))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        image.save(args.out, optimize=True)
    out = args.out.resolve()
    print(f"{out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}  {image.width} × {image.height}")


if __name__ == "__main__":
    main()
