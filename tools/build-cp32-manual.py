# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown>=3.6", "pypdf>=5"]
# ///
"""Typeset the English Lucky CP32 manual as an A4 PDF in the site's style.

    uv run tools/build-cp32-manual.py

The text is tools/cp32-manual/manual.md, translated from the scans of the
Japanese manual (static/downloads/lucky_cp32_manual_jp_original.pdf), with
the figures cut from them in tools/cp32-manual/figures/. Each `##` heading
starts a numbered block; its `data-jp` names the pages of the Japanese
manual it comes from, which the rail prints. Links to `#id` gain the page
of that section, so the PDF is printed until the pages settle: the first
pass finds them, the next prints them, and the last confirms them.

Writes static/downloads/lucky_cp32_manual_en_translated.pdf, the file the
Darkroom page links.
"""

import html
import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
SOURCE = ROOT / "tools/cp32-manual"
FONTS = ROOT / "static/fonts/plex"
PDF = ROOT / "static/downloads/lucky_cp32_manual_en_translated.pdf"
TITLE = "Lucky CP32 Operation Manual"
DEK = "An English translation of the Japanese manual for the Lucky CP32 color paper processor."
TRANSLATED = "2025-01-09"
REVISED = "2026-11-03"
FACES = (("IBM Plex Sans", 400, "normal", "IBMPlexSans-Regular"),
         ("IBM Plex Sans", 400, "italic", "IBMPlexSans-Italic"),
         ("IBM Plex Sans", 600, "normal", "IBMPlexSans-SemiBold"),
         ("IBM Plex Mono", 400, "normal", "IBMPlexMono-Regular"),
         ("IBM Plex Mono", 500, "normal", "IBMPlexMono-Medium"))

# Panel at print size: the site's tokens and its rail-and-column layout,
# on A4. Plex lacks the Japanese labels quoted from the scans; they fall
# back to the system's Hiragino.
STYLE = """
@page { size: A4; margin: 15mm 16mm 18mm;
  @bottom-left { content: "%(title)s"; font: 7.5pt "IBM Plex Sans"; color: #6e6e6e; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 7.5pt "IBM Plex Mono"; color: #6e6e6e; } }
* { box-sizing: border-box; }
html { color: #000; background: #fff; font: 9.5pt/13.5pt "IBM Plex Sans", "Hiragino Sans", sans-serif;
  font-variant-numeric: tabular-nums; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; }
.n, time { font-family: "IBM Plex Mono", monospace; }
a { color: inherit; text-decoration: none; }
.col a { text-decoration: underline; text-decoration-thickness: .2mm; text-underline-offset: .6mm; }
.pg { color: #555; }
strong { font-weight: 600; }

.head, .block { position: relative; padding-left: 40mm; }
.rail { position: absolute; left: 0; top: 0; width: 34mm; display: flex; flex-direction: column;
  align-items: flex-end; text-align: right; font-size: 7.5pt; line-height: 10.5pt; color: #6e6e6e; }
.rail .n { font-size: 9pt; line-height: 15pt; color: #000; }
.signal { display: inline-flex; align-items: center; gap: 1.6mm; color: #000; margin-bottom: 3mm; }
.signal::before { content: ""; width: 2mm; height: 2mm; background: #ff4f00; }

.head { padding-top: 6mm; }
h1 { font-size: 22pt; line-height: 28pt; font-weight: 400; margin: 0 0 2mm; }
.dek { font-size: 11.5pt; line-height: 16pt; color: #555; margin: 0 0 5mm; max-width: 120mm; }
.about { font-size: 8pt; line-height: 11.5pt; color: #555; max-width: 120mm; margin: 0 0 9mm; }
.contents h2 { margin-bottom: 2mm; }
.contents ol { list-style: none; margin: 0; padding: 0; }
.contents li { display: grid; grid-template-columns: 8mm 1fr 10mm; padding: .9mm 0; margin: 0; }
.contents li::before { content: none; }
.contents .n { color: #6e6e6e; }
.contents .n:last-child { color: #000; text-align: right; }

.block { break-before: auto; margin-top: 9mm; }
.head + .block, .block.page { break-before: page; margin-top: 0; }
h2 { font-size: 11pt; line-height: 15pt; font-weight: 600; margin: 0 0 3mm; break-after: avoid; position: relative; }
h3 { font-size: 9.5pt; font-style: italic; font-weight: 400; margin: 4.5mm 0 1.5mm; break-after: avoid; }
p { margin: 0 0 2.2mm; }
h4 { font-size: 8.5pt; font-style: italic; font-weight: 400; color: #555; margin: 4mm 0 1mm; break-after: avoid; }
ul { margin: 0 0 2.2mm; padding-left: 4.2mm; }
li { margin: 0 0 .8mm; }
.col > ol { list-style: none; margin: 0 0 2mm; padding: 0; counter-reset: step; }
.col > ol > li { counter-increment: step; position: relative; padding-left: 7mm; margin-bottom: 3mm; break-inside: avoid; }
.col > ol > li::before { content: counter(step); position: absolute; left: 0; font: 500 9.5pt/13.5pt "IBM Plex Mono"; }
.col > ol > li > strong:first-child, .col > ol > li > p:first-child > strong:first-child { font-weight: 600; }
li ol { list-style: none; padding-left: 0; margin: .8mm 0 1mm; counter-reset: sub; }
li ol > li { counter-increment: sub; position: relative; padding-left: 5mm; }
li ol > li::before { content: counter(sub, lower-alpha); position: absolute; left: 0; font-family: "IBM Plex Mono"; color: #555; }
li > p { margin-bottom: 1.2mm; }

.lcd { display: inline-block; vertical-align: middle; margin: .6mm .5mm; padding: 1mm 2.2mm;
  background: #161616; color: #e6e6e6; border-radius: .6mm;
  font: 500 7.5pt/9pt "IBM Plex Mono", monospace; white-space: nowrap; }
.nw { white-space: nowrap; }
.formula { font: 10.5pt "IBM Plex Mono", monospace; margin: 2.5mm 0 2.5mm 7mm; break-before: avoid; break-after: avoid; }

.figs { display: grid; gap: 4mm; margin: 3mm 0 5mm; align-items: start; }
.figs.one { grid-template-columns: 1fr; }
.figs.one.narrow { width: 62%%; }
.figs.two, .figs.four { grid-template-columns: 1fr 1fr; }
.figs.three { grid-template-columns: 1fr 1fr 1fr; }
figure { margin: 0; break-inside: avoid; }
figure img { display: block; width: 100%%; height: auto; }
.figs.one img { width: auto; max-width: 100%%; max-height: 95mm; }
.figs.one.tall img { max-height: 205mm; }
figcaption { margin-top: 1.5mm; font-size: 7.5pt; line-height: 10.5pt; color: #6e6e6e; }
figcaption b { font-weight: 400; color: #000; }

table { width: 100%%; border-collapse: collapse; margin: 1mm 0 4mm; font-size: 8.5pt; line-height: 12pt; break-inside: avoid; }
th { font-weight: 600; text-align: left; vertical-align: bottom; border-bottom: .3mm solid #000; padding: 0 3mm 1.2mm 0; }
td { vertical-align: top; border-bottom: .2mm solid #d9d9d9; padding: 1.2mm 3mm 1.2mm 0; }
tr:last-child td { border-bottom: 0; }
.table td:first-child { min-width: 40mm; }
td[style*="right"] { white-space: nowrap; }
th:last-child, td:last-child { padding-right: 0; }
.table.narrow table { width: 62%%; }
.specs thead { display: none; }
.specs td:first-child, .key td:first-child { width: 36mm; color: #555; }
.key td:first-child { width: 58mm; }

.trouble { columns: 2; column-gap: 7mm; }
.trouble h3 { margin-top: 0; padding-top: 3mm; break-inside: avoid; }
.trouble ul { break-inside: avoid; margin-bottom: 1mm; }

.marker { position: absolute; left: 0; top: 0; font-size: 1pt; color: #fff; }
"""


def faces():
    return "".join(f'@font-face {{ font-family: "{family}"; font-weight: {weight}; font-style: {style}; '
                   f'src: url("{(FONTS / f"{name}.woff2").as_uri()}") format("woff2"); }}\n'
                   for family, weight, style, name in FACES)


def figures(body):
    # Markdown gives an image paragraph; the page wants a figure with the
    # alt text as its caption and "Figure n" in ink.
    def figure(match):
        alt, src = html.unescape(match.group(1)), match.group(2)
        number = re.match(r"(Figure \d+)\.\s*(.*)", alt)
        caption = (f"<b>{number.group(1)}.</b> {html.escape(number.group(2))}" if number
                   else html.escape(alt))
        uri = (SOURCE / src).resolve().as_uri()
        return f'<figure><img src="{uri}" alt=""><figcaption>{caption}</figcaption></figure>'
    return re.sub(r'<p><img alt="([^"]*)" src="([^"]+)" ?/?></p>', figure, body)


def blocks(body, pages, markers):
    """Split the body at each h2 into a numbered block with its rail."""
    parts = re.split(r"(?=<h2[ >])", body)
    out, contents = [], []
    for number, part in enumerate((p for p in parts if p.startswith("<h2")), start=2):
        head = re.match(r"<h2([^>]*)>(.*?)</h2>", part, re.S)
        attrs, title = head.group(1), head.group(2)
        ident = re.search(r'id="([^"]+)"', attrs).group(1)
        jp = re.search(r'data-jp="([^"]+)"', attrs)
        page = " page" if 'data-break="page"' in attrs else ""
        mark = f'<span class="marker">@@{ident}@@</span>' if markers else ""
        rail = (f'<span class="n">{number:02d}</span>'
                + (f'<span>Japanese manual</span><span>page <span class="n">{jp.group(1)}</span></span>'
                   if jp else ""))
        rest = part[head.end():]
        out.append(f'<section class="block{page}"><div class="rail">{rail}</div><div class="col">'
                   f'<h2 id="{ident}">{mark}{title}</h2>{rest}</div></section>')
        contents.append((number, ident, re.sub(r"<[^>]+>", "", title)))
    return "".join(out), contents


def page_of(pages, ident):
    return str(pages.get(ident, "00"))


def references(body, pages):
    # Each link to a section reads on in print with that section's page.
    return re.sub(r'(<a href="#([^"]+)">.*?</a>)',
                  lambda m: f'{m.group(1)}<span class="pg"> (page <span class="n">{page_of(pages, m.group(2))}</span>)</span>',
                  body)


def document(pages, markers):
    source = (SOURCE / "manual.md").read_text()
    body = markdown.markdown(source, extensions=["tables", "attr_list", "md_in_html", "sane_lists", "nl2br"])
    body = figures(body)
    # A list that resumes after a row of figures starts its counter there.
    body = re.sub(r'<ol start="(\d+)">',
                  lambda m: f'<ol start="{m.group(1)}" style="counter-reset: step {int(m.group(1)) - 1}">', body)
    body, contents = blocks(body, pages, markers)
    body = references(body, pages)
    rows = "".join(f'<li><span class="n">{number:02d}</span><a href="#{ident}">{title}</a>'
                   f'<span class="n">{page_of(pages, ident)}</span></li>'
                   for number, ident, title in contents)
    style = STYLE % {"title": TITLE}
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>{TITLE}</title>
<style>{faces()}{style}</style>
<header class="head">
<div class="rail"><span class="signal">ttvl.co</span><span>Darkroom · Manual</span>
<span>Translated <time>{TRANSLATED}</time></span><span>Revised <time>{REVISED}</time></span></div>
<h1>{TITLE}</h1>
<p class="dek">{DEK}</p>
<p class="about">Translated by Toto Tvalavadze from the scans of the Japanese manual, with some Japanese and a few AI tools, and checked page by page against them. The scans are at ttvl.co/downloads/lucky_cp32_manual_jp_original.pdf; each section names the pages it comes from. Untranslated: the procedure chart (page 5) and the Kodak chemistry leaflet (page 22).</p>
<nav class="contents"><h2>Contents</h2><ol>{rows}</ol></nav>
</header>
{body}
</html>"""


def render(page, pdf, chrome):
    with tempfile.TemporaryDirectory(prefix="cp32-") as tmp:
        source = Path(tmp) / "manual.html"
        source.write_text(page)
        proc = subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu",
                              "--allow-file-access-from-files", f"--user-data-dir={tmp}/chrome",
                              "--no-pdf-header-footer", "--virtual-time-budget=5000",
                              f"--print-to-pdf={pdf}", source.as_uri()],
                              capture_output=True, text=True, timeout=90)
        if proc.returncode or not Path(pdf).is_file():
            raise RuntimeError(proc.stderr)


def sections_by_page(pdf):
    pages = {}
    for number, page in enumerate(PdfReader(pdf).pages, start=1):
        for ident in re.findall(r"@@([\w-]+)@@", page.extract_text() or ""):
            pages.setdefault(ident, number)
    return pages


def main():
    spec = importlib.util.spec_from_file_location("drawing_png", ROOT / "tools/drawing-png.py")
    drawing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(drawing)
    chrome = drawing.browser()
    pages = {}
    with tempfile.TemporaryDirectory(prefix="cp32-pass-") as tmp:
        draft = Path(tmp) / "draft.pdf"
        for _ in range(4):
            render(document(pages, markers=True), draft, chrome)
            found = sections_by_page(draft)
            if found == pages:
                break
            pages = found
        else:
            raise RuntimeError("The section pages did not settle.")
    render(document(pages, markers=False), PDF, chrome)
    count = len(PdfReader(PDF).pages)
    print(f"Wrote {PDF.relative_to(ROOT)}: {count} pages, {len(pages)} sections")


if __name__ == "__main__":
    main()
