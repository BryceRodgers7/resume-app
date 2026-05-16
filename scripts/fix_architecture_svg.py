#!/usr/bin/env python3
"""Fix Mermaid SVG exports that have no root viewBox and a baked-in pan/zoom matrix.

Some Mermaid export tools (notably the "Save as SVG" button in interactive
viewers built on svg-pan-zoom) produce SVGs that:

  1. Have ``width="100%" height="100%"`` and NO root ``viewBox`` — so the SVG
     has zero intrinsic size and renders as a blank rectangle in any
     container that doesn't supply a fixed height (Cursor preview,
     Streamlit's components.html, etc.).
  2. Have an ``svg-pan-zoom_viewport`` group with a transform matrix that
     captures whatever pan/zoom state was active at export time — leaving
     the diagram shrunken and offset when rendered.

This script patches both problems:

  * Adds a root ``viewBox`` sized to contain the natural content (estimated
    from the maximum ``translate(x, y)`` coordinates inside the file).
  * Resets the pan/zoom matrix to identity.
  * Drops the root ``height="100%"`` attribute that forces a 0-px collapse.

The script is idempotent — running it on an already-patched file is a no-op.

Usage:
    python scripts/fix_architecture_svg.py path/to/exported.svg
    python scripts/fix_architecture_svg.py path/to/exported.svg --output fixed.svg
    python scripts/fix_architecture_svg.py path/to/exported.svg --no-backup
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple

# Padding (in SVG user units) added around the true content bounds so the
# viewBox doesn't visually clip a stroke edge or anti-aliased pixel. With
# the proper tree-walking estimator below, this only needs to be a small
# safety margin — not a guess for unknown node widths.
VIEWBOX_PADDING = 60

# Fallback viewBox dimensions when bounds estimation finds nothing.
FALLBACK_VIEWBOX = (4760, 1600)

SVG_NS = "{http://www.w3.org/2000/svg}"
_TRANSLATE_RE = re.compile(r"translate\(([-\d.]+)[,\s]+([-\d.]+)\)")


def _local_tag(elem: ET.Element) -> str:
    return elem.tag[len(SVG_NS):] if elem.tag.startswith(SVG_NS) else elem.tag


def _parse_translate(transform: str) -> Tuple[float, float]:
    if not transform:
        return 0.0, 0.0
    m = _TRANSLATE_RE.search(transform)
    return (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)


def estimate_content_bounds(svg_text: str) -> Tuple[int, int]:
    """Compute the natural content extent by walking the SVG tree.

    For every ``<rect>``, the absolute right/bottom edge is::

        absolute_right  = sum(parent translates) + rect.x + rect.width
        absolute_bottom = sum(parent translates) + rect.y + rect.height

    Tracking the cumulative translate stack and taking the max across every
    rect gives the true bounding box of the rendered content — unlike a
    naive translate-position scan, which under-counts because translates
    mark where each node is placed, not where its right/bottom edge is.

    Path/line elements are ignored: Mermaid keeps edge segments within
    node-bounded clusters in practice, and parsing path ``d`` data would be
    significant extra complexity for negligible gain.
    """
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError:
        return FALLBACK_VIEWBOX

    right = 0.0
    bottom = 0.0

    def walk(elem: ET.Element, cx: float, cy: float) -> None:
        nonlocal right, bottom
        dx, dy = _parse_translate(elem.get("transform", ""))
        cx += dx
        cy += dy
        if _local_tag(elem) == "rect":
            try:
                rx = float(elem.get("x", "0"))
                ry = float(elem.get("y", "0"))
                rw = float(elem.get("width", "0"))
                rh = float(elem.get("height", "0"))
                right = max(right, cx + rx + rw)
                bottom = max(bottom, cy + ry + rh)
            except ValueError:
                pass
        for child in elem:
            walk(child, cx, cy)

    walk(root, 0.0, 0.0)

    if right <= 0 or bottom <= 0:
        return FALLBACK_VIEWBOX
    return int(right) + VIEWBOX_PADDING, int(bottom) + VIEWBOX_PADDING


def patch_svg(svg_text: str) -> Tuple[str, List[str]]:
    """Apply both patches. Returns (patched_text, list_of_change_descriptions).

    Idempotent: when a patch is unnecessary, it's skipped.
    """
    changes: List[str] = []
    out = svg_text

    # ----- Patch 1: root <svg> — drop height="100%", add viewBox + preserveAspectRatio
    root_match = re.search(r"<svg\b[^>]*>", out)
    if not root_match:
        raise ValueError("No root <svg> element found — is this really an SVG file?")
    root_tag = root_match.group(0)
    new_root = root_tag

    if "viewBox=" not in new_root:
        w, h = estimate_content_bounds(out)
        # Remove an existing height="100%" attribute if present
        new_root = re.sub(r'\s*\bheight="100%"', "", new_root)
        # Inject viewBox + preserveAspectRatio just before the closing '>'
        new_root = (
            new_root.rstrip(">").rstrip()
            + f' viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet">'
        )
        changes.append(
            f'added viewBox="0 0 {w} {h}" + preserveAspectRatio="xMidYMid meet" '
            f'on root <svg> (and removed height="100%" if present)'
        )

    if new_root != root_tag:
        out = out.replace(root_tag, new_root, 1)

    # ----- Patch 2: reset svg-pan-zoom_viewport matrix to identity
    matrix_pattern = re.compile(
        r'(class="svg-pan-zoom_viewport"\s+transform=")matrix\([^)]+\)(")'
    )
    matrix_match = matrix_pattern.search(out)
    if matrix_match and "matrix(1,0,0,1,0,0)" not in matrix_match.group(0):
        out = matrix_pattern.sub(r"\1matrix(1,0,0,1,0,0)\2", out)
        # Also normalise the duplicate inline style="transform: matrix(...)"
        # that the same exporter writes alongside the attribute.
        out = re.sub(
            r'(class="svg-pan-zoom_viewport"[^>]*style="[^"]*?transform:\s*)matrix\([^)]+\)',
            r"\1matrix(1, 0, 0, 1, 0, 0)",
            out,
        )
        changes.append("reset svg-pan-zoom_viewport matrix to identity")

    return out, changes


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Patch a Mermaid SVG export so it has a usable root viewBox "
            "and no baked-in pan/zoom matrix."
        ),
    )
    parser.add_argument("path", type=Path, help="SVG file to patch")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Write patched SVG to this path instead of editing in place.",
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="Do not create a .bak file before editing in place.",
    )
    args = parser.parse_args(argv)

    if not args.path.is_file():
        print(f"error: not a file: {args.path}", file=sys.stderr)
        return 2

    svg_text = args.path.read_text(encoding="utf-8")
    try:
        patched, changes = patch_svg(svg_text)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if not changes:
        print(f"{args.path}: already patched — nothing to do.")
        return 0

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(patched, encoding="utf-8")
        target_msg = f"wrote patched SVG to {args.output}"
    else:
        if not args.no_backup:
            backup = args.path.with_suffix(args.path.suffix + ".bak")
            shutil.copyfile(args.path, backup)
            print(f"backup: {backup}")
        args.path.write_text(patched, encoding="utf-8")
        target_msg = f"patched in place: {args.path}"

    print(target_msg)
    for change in changes:
        print(f"  - {change}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
