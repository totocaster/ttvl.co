# /// script
# requires-python = ">=3.11"
# dependencies = ["imageio-ffmpeg"]
# ///
"""Make the email stand-in for a clip: a smaller, lower-fidelity GIF.

Email clients don't play video, so a Flâneur dispatch's email output shows
a clip as the GIF that sits beside its MP4 under the same name
(clip.mp4 -> clip.gif), falling back to the poster frame when there is none
(layouts/flaneur/single.email.html). The web pages keep the MP4.

    uv run tools/clip-gif.py static/visuals/research/ambient-computing/2026-10-04-find-a-place.mp4
    uv run tools/clip-gif.py --end 17.5 --speed 1.5 --fps 8 --colors 64 static/flaneur/017_jinny_walk.mp4

The defaults fit the email's 600 px column at 10 frames per second and 96
colors, with one palette per clip. Lower --fps, --width, or --colors, raise
--speed, or trim with --start and --end when a GIF comes out heavy (a moving
camera is costly); aim for a few megabytes at most, since readers on phones
download every frame. Classic Outlook for Windows shows only the first frame,
so it should make sense on its own.
"""

import argparse
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg


def make_gif(src: Path, args: argparse.Namespace) -> Path:
    dst = src.with_suffix(".gif")
    trim = []
    if args.start is not None:
        trim += ["-ss", str(args.start)]
    if args.end is not None:
        trim += ["-to", str(args.end)]
    graph = (
        f"setpts=PTS/{args.speed},fps={args.fps},scale={args.width}:-2:flags=lanczos,split[a][b];"
        f"[a]palettegen=max_colors={args.colors}:stats_mode=diff[p];"
        "[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle"
    )
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", *trim, "-i", str(src),
         "-filter_complex", graph, "-loop", "0", str(dst)],
        check=True,
    )
    return dst


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("clips", nargs="+", type=Path, help="MP4 files under static/")
    parser.add_argument("--width", type=int, default=600, help="pixels (default 600)")
    parser.add_argument("--fps", type=int, default=10, help="frames per second (default 10)")
    parser.add_argument("--colors", type=int, default=96, help="palette size, 2-256 (default 96)")
    parser.add_argument("--speed", type=float, default=1.0, help="playback speed, e.g. 1.5 (default 1)")
    parser.add_argument("--start", type=float, help="seconds into the clip to begin")
    parser.add_argument("--end", type=float, help="seconds into the clip to stop")
    args = parser.parse_args()

    for src in args.clips:
        if src.suffix.lower() != ".mp4" or not src.is_file():
            print(f"skipping {src}: not an MP4 file", file=sys.stderr)
            continue
        dst = make_gif(src, args)
        print(f"{dst}  {dst.stat().st_size / 1_000_000:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
