#!/usr/bin/env python3
"""Render the example deck and verify PDF pagination and canvas geometry."""

import shutil
import subprocess
import sys
import tempfile
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "carousel" / "briefs" / "example-brief.yaml"


def main():
    chrome = next(
        (
            candidate
            for candidate in (
                shutil.which("google-chrome"),
                shutil.which("chromium"),
                shutil.which("chromium-browser"),
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            )
            if candidate and Path(candidate).exists()
        ),
        None,
    )
    if not chrome:
        raise SystemExit("Chrome/Chromium is required for the render smoke test")

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "carousel" / "generate.py"),
                str(BRIEF),
                "--out",
                tmp,
                "--chrome",
                chrome,
            ],
            check=True,
        )
        pdfs = list(Path(tmp).glob("*.pdf"))
        if len(pdfs) != 1:
            raise AssertionError(f"expected one PDF, found {len(pdfs)}")

        pdf = pdfs[0].read_bytes()
        pages = re.findall(rb"/Type\s*/Page(?!s)\b", pdf)
        if len(pages) != 9:
            raise AssertionError(f"expected 9 pages, found {len(pages)}")

        boxes = re.findall(
            rb"/MediaBox\s*\[\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)\s*\]",
            pdf,
        )
        if not boxes:
            raise AssertionError("PDF has no readable MediaBox")
        for index, (raw_width, raw_height) in enumerate(boxes, 1):
            width = float(raw_width)
            height = float(raw_height)
            if not height > width:
                raise AssertionError(
                    f"page {index} is not portrait: {width:.1f} × {height:.1f}"
                )
            if abs((width / height) - 0.8) > 0.01:
                raise AssertionError(
                    f"page {index} has wrong aspect ratio: {width:.1f} × {height:.1f}"
                )

    print("render smoke test: 9 portrait pages at 4:5")


if __name__ == "__main__":
    main()
