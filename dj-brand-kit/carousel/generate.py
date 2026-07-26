#!/usr/bin/env python3
"""Generate a LinkedIn carousel PDF from a story brief.

Usage:
    python3 generate.py path/to/brief.yaml [--out DIR] [--keep-html] [--chrome PATH]

Reads the brief (format: dj-brand-kit/guidance/08-carousel-application.md),
validates the fixed deck shape, renders slides via renderer/slides.html, and
prints to a single 1080×1350 PDF with headless Chrome — vector text, fonts
embedded, ready to upload as a LinkedIn document post.

Requires: PyYAML, Google Chrome (or chromium on PATH). No other dependencies.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


def slugify(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", str(s).lower())).strip("-")


def script_safe_json(value):
    """Serialize JSON without allowing text to close the bootstrap script."""
    return json.dumps(value).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def output_name(brief):
    """Structured, sortable PDF filename — one deterministic name per deck.

        {series}-{sector}[-{chapter}]-c{NN}-{slug}.pdf

    Segments come straight from the brief: series and sector are the eyebrow
    fields, `chapter` is the optional sub-theme (e.g. Rentals), `carousel` is
    the number in the series (zero-padded), and `slug` is the title. See the
    README 'Output filename' section. Falls back to <slug>.pdf if `carousel`
    is absent, so old briefs still render.
    """
    if brief.get("carousel") is None:
        return f"{slugify(brief['slug'])}.pdf"
    parts = [slugify(brief["series"]), slugify(brief["sector"])]
    if brief.get("chapter"):
        parts.append(slugify(brief["chapter"]))
    parts.append(f"c{int(brief['carousel']):02d}")
    parts.append(slugify(brief["slug"]))
    return "-".join(parts) + ".pdf"

KIT_ROOT = Path(__file__).resolve().parent
TEMPLATE = KIT_ROOT / "renderer" / "slides.html"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "chromium",
    "chromium-browser",
]

BEAT_TYPES = {"big_number", "chart", "concept"}
CHART_KINDS = {"bar", "slope", "beeswarm", "scatter", "table"}
SYNTHESIS_KINDS = CHART_KINDS | {"big_number", "concept"}
ACCENT_FLAGS = ("protagonist", "highlight", "accent")
INTERIOR_THEMES = {"parchment", "navy", "carbon"}   # alabaster: Context + final slide only
CTA_THEMES = INTERIOR_THEMES | {"alabaster"}


def fail(msg):
    sys.exit(f"Brief invalid: {msg}")


def check_chart(spec, where):
    if spec.get("kind") not in CHART_KINDS:
        fail(f"{where}: chart kind must be one of {sorted(CHART_KINDS)}")
    if not spec.get("data"):
        fail(f"{where}: chart needs 'data'")
    # Every chart is preceded by a setup slide (what the data is). It draws from
    # `setup`, falling back to `title`, so one of them must be present.
    if not spec.get("setup") and not spec.get("title"):
        fail(f"{where}: chart needs a 'setup' line (the framing slide before the chart) or a 'title'")
    if spec["kind"] in ("beeswarm", "scatter", "table"):
        # Distribution / relationship / table charts: colour marks a group, the
        # few labelled points worth reading, or nothing at all — not a single
        # named series. The one-accent rule below governs bar/slope only.
        if spec["kind"] == "table" and not spec.get("columns"):
            fail(f"{where}: table needs 'columns' (header row) and 'data' (rows)")
        return
    # Directional colour: with 2+ series, exactly one element carries the
    # accent — uniform accent flattens the read, zero accents directs nothing.
    rows = spec["data"]
    if len(rows) > 1:
        accented = sum(1 for d in rows if any(d.get(f) for f in ACCENT_FLAGS))
        if accented != 1:
            fail(f"{where}: mark exactly one series with protagonist/highlight/accent "
                 f"(found {accented} of {len(rows)}) — colour directs the eye, it doesn't decorate")


def check_theme(spec, where):
    theme = spec.get("theme", "parchment")
    if theme not in INTERIOR_THEMES:
        fail(f"{where}: theme must be one of {sorted(INTERIOR_THEMES)} — "
             "Alabaster is reserved for the Context and final (CTA) slides")


def check_data_slide(spec, where):
    if not spec.get("judgment"):
        fail(f"{where}: needs a 'judgment' — one sentence of interpretation. "
             "Numbers without interpretation are a dashboard, not a DataJockey artifact")
    check_theme(spec, where)


def check_concept(spec, where):
    # Explanatory slide — a ladder of steps, or two parallel ladders. It carries
    # an argument, not a figure, so it is exempt from the judgment rule.
    if spec.get("columns"):
        for c in spec["columns"]:
            if not (c.get("label") and isinstance(c.get("steps"), list) and c["steps"]):
                fail(f"{where}: each concept column needs a 'label' and non-empty 'steps'")
    elif spec.get("ladder"):
        if not (isinstance(spec["ladder"], list) and spec["ladder"]):
            fail(f"{where}: concept 'ladder' must be a non-empty list of steps")
    elif not spec.get("body"):
        fail(f"{where}: concept needs 'columns' (parallel ladders), 'ladder' (steps), "
             "or a 'body' punchline (a title + one supporting line)")
    check_theme(spec, where)


def validate(brief):
    for key in ("project", "slug", "series", "sector", "takeaway", "source",
                "hook", "beats", "synthesis", "so_what", "cta"):
        if key not in brief:
            fail(f"missing top-level field '{key}' "
                 "(series/sector/takeaway feed the every-slide eyebrow)")

    # carousel/chapter drive the structured output filename (see output_name)
    if brief.get("carousel") is not None:
        try:
            int(brief["carousel"])
        except (TypeError, ValueError):
            fail("carousel must be a whole number — its position in the series (feeds the filename)")

    beats = brief["beats"]
    if not isinstance(beats, list) or not 1 <= len(beats) <= 5:
        fail("beats must be a list of 1–5 slides (deck shape is fixed)")

    for i, beat in enumerate(beats, 1):
        t = beat.get("type")
        if t not in BEAT_TYPES:
            fail(f"beat {i}: type must be one of {sorted(BEAT_TYPES)}")
        if t == "big_number" and not (beat.get("value") and beat.get("label")):
            fail(f"beat {i}: big_number needs 'value' and 'label'")
        if t == "chart":
            check_chart(beat, f"beat {i}")
        if t == "concept":
            check_concept(beat, f"beat {i}")
        else:
            check_data_slide(beat, f"beat {i}")

    syn = brief["synthesis"]
    if syn.get("kind") not in SYNTHESIS_KINDS:
        fail(f"synthesis kind must be one of {sorted(SYNTHESIS_KINDS)}")
    if syn["kind"] == "concept":
        check_concept(syn, "synthesis")
    else:
        if syn["kind"] in CHART_KINDS:
            check_chart(syn, "synthesis")
        check_data_slide(syn, "synthesis")
    hook = brief["hook"]
    # Every deck leads with a number — the Honey Bronze hero figure that stops
    # the scroll. A bare-string hook (no number) is no longer allowed.
    if isinstance(hook, str):
        fail("hook needs a number — use the object form "
             "(headline / number / number_label). Every deck leads with a "
             "Honey Bronze hero figure, so a statement-only hook isn't allowed.")
    elif isinstance(hook, dict):
        for field in ("headline", "number", "number_label"):
            if not hook.get(field):
                fail(f"hook.{field} is required "
                     "(headline: statement · number: key metric · number_label: what it measures)")
        if len(hook["headline"]) > 140:
            fail(f"hook.headline is {len(hook['headline'])} chars — max 140")
        if "puzzle" not in brief:
            fail("puzzle is required alongside the hook — "
                 "add puzzle.question and puzzle.misconception")
    else:
        fail("hook must be an object with headline, number, number_label")

    puzzle = brief.get("puzzle")
    if puzzle is not None:
        if not isinstance(puzzle, dict):
            fail("puzzle must be an object with question and misconception")
        if not puzzle.get("question"):
            fail("puzzle.question is required")
        if not puzzle.get("misconception"):
            fail("puzzle.misconception is required")

    # Context slide — optional, always Alabaster. Expands the eyebrow: what
    # the series tracks and its event anchor, before the numbers.
    context = brief.get("context")
    if context is not None:
        if not isinstance(context, str) or not context.strip():
            fail("context, when present, must be a plain statement of what the "
                 "series tracks — it renders as slide 2 on Alabaster")
        if len(context) > 240:
            fail(f"context is {len(context)} chars — two or three short sentences "
                 "expanding the eyebrow, not an essay (max 240)")

    if not isinstance(brief["so_what"], str) or not brief["so_what"].strip():
        fail("so_what must be a plain-English statement of what decision or "
             "action these numbers inform — the slide the deck exists for")
    if "actionable insight" in brief["so_what"].lower():
        fail("so_what: 'actionable insight' is banned vocabulary "
             "(01-voice-and-principles.md) — say what the reader can decide, plainly")

    cta = brief["cta"]
    ok = cta == "default" or (isinstance(cta, dict) and (cta.get("next") or cta.get("theme")))
    if not ok:
        fail("cta must be 'default' (directional series-rotation close) or "
             "{next: '...'} naming a concrete upcoming piece")
    if isinstance(cta, dict) and cta.get("theme", "navy") not in CTA_THEMES:
        fail(f"cta theme must be one of {sorted(CTA_THEMES)}")


def find_chrome(override):
    if override:
        return override
    for cand in CHROME_CANDIDATES:
        if Path(cand).exists() or shutil.which(cand):
            return cand
    sys.exit("No Chrome/Chromium found — pass --chrome /path/to/binary")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("brief", type=Path)
    ap.add_argument("--out", type=Path, default=None,
                    help="output directory (default: <brief dir>/out)")
    ap.add_argument("--keep-html", action="store_true",
                    help="keep the rendered HTML for inspection in a browser")
    ap.add_argument("--chrome", default=None, help="Chrome/Chromium binary override")
    ap.add_argument("--validate-only", action="store_true",
                    help="validate the brief and exit without requiring Chrome")
    args = ap.parse_args()

    brief = yaml.safe_load(args.brief.read_text())
    validate(brief)
    if args.validate_only:
        print(f"{args.brief}: valid")
        return

    out_dir = args.out or (args.brief.resolve().parent / "out")
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = (out_dir / output_name(brief)).resolve()
    chrome = find_chrome(args.chrome)

    # Build the render page inside renderer/ so its relative paths
    # (tokens, fonts, logo assets) resolve over file://
    html = TEMPLATE.read_text().replace("{{BRIEF_JSON}}", script_safe_json(brief))
    build_page = TEMPLATE.parent / f".build-{slugify(brief['slug'])}.html"
    build_page.write_text(html)

    cmd = [
        chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        "--virtual-time-budget=5000",          # let fonts finish loading
        f"--print-to-pdf={pdf_path}",
        build_page.resolve().as_uri(),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        if not args.keep_html:
            build_page.unlink(missing_ok=True)

    if args.keep_html:
        print(f"render page kept: {build_page}")

    if result.returncode != 0 or not pdf_path.exists():
        sys.exit(f"Chrome render failed:\n{result.stderr}")

    chart_beats = sum(1 for b in brief["beats"] if b.get("type") == "chart")
    # hook + synthesis + so-what + CTA + appendix = 5; +1 setup per chart; context disabled
    n_slides = 5 + len(brief["beats"]) + chart_beats + (1 if brief.get("puzzle") else 0)
    print(f"{pdf_path}  ({n_slides} slides, {pdf_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
