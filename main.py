#!/usr/bin/env python3
"""Generate multi-scale dot grid PDFs with zero margins."""

import argparse
from pathlib import Path

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, inch, mm
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"

# Grid spacings as multiples of one base unit (1 cm, 1 inch, or 1/4 inch).
SPACING_4X_BASE = 4
SPACING_1X_BASE = 1
SPACING_HALF_BASE = 0.5
SPACING_QUARTER_BASE = 0.25
SPACING_THIRD_BASE = 1 / 3

# Dot sizes are fixed physical dimensions (original cm-based layout), not tied to -base.
DOT_RADIUS_1X_MM = 0.35
DOT_RADIUS_4X_OF_1X = 2 * 0.8
DOT_RADIUS_THIRD_OVERLAY_OF_BASE_QUARTER = 2.0

DOT_DARKNESS_AT_1X_BASE = 1 / 3
COLOR_EVERY_THIRD_ON_1X_BASE = (0.72, 0.92, 0.72)
COLOR_ON_THIRD_BASE_GRID = (0.92, 0.22, 0.22)

EVERY_THIRD_ON_1X_BASE = 3
PAGE_COUNT = 2

BASE_CHOICES = ("cm", "inches", "quarter-inch")
PAPER_CHOICES = ("letter", "a4")

# CLI value -> segment in fractional-grid-{base}-{paper}.pdf
BASE_NAME_FOR_FILE: dict[str, str] = {
    "cm": "cm",
    "inches": "inch",
    "quarter-inch": "quarter-inch",
}


def output_path(base_unit: str, paper: str) -> Path:
    base_name = BASE_NAME_FOR_FILE[base_unit]
    return OUTPUT_DIR / f"fractional-grid-{base_name}-{paper}.pdf"


def _one_base_unit_points(base_unit: str) -> float:
    if base_unit == "quarter-inch":
        return inch / 4
    if base_unit == "inches":
        return inch
    if base_unit == "cm":
        return cm
    raise ValueError(f"unsupported base unit: {base_unit!r}")


def _page_size(paper: str) -> tuple[float, float]:
    if paper == "a4":
        return A4
    if paper == "letter":
        return letter
    raise ValueError(f"unsupported paper: {paper!r}")


def _on_grid(
    value: float, step: float, origin: float = 0.0, tol: float = 1e-4
) -> bool:
    n = round((value - origin) / step)
    return abs(value - origin - n * step) <= tol


def _axis_positions_x(extent: float, step: float, tol: float = 1e-4) -> list[float]:
    """Horizontal positions from the left edge (x=0)."""
    positions: list[float] = []
    v = 0.0
    while v <= extent + tol:
        positions.append(v)
        v += step
    if not positions or positions[-1] < extent - tol:
        positions.append(extent)
    return positions


def _axis_positions_y(page_h: float, step: float, tol: float = 1e-4) -> list[float]:
    """Vertical positions from the top edge (y=page_h) down to y=0."""
    positions: list[float] = []
    v = page_h
    while v >= -tol:
        positions.append(v)
        v -= step
    if not positions or positions[-1] > tol:
        positions.append(0.0)
    return positions


def _dot_style(
    x: float,
    y: float,
    page_h: float,
    step_4x: float,
    step_1x: float,
    step_half: float,
    radius_4x: float,
    radius_1x: float,
    radius_half: float,
    radius_quarter: float,
) -> tuple[float, float, str]:
    if _on_grid(x, step_4x, 0.0) and _on_grid(y, step_4x, page_h):
        darkness = min(1.0, DOT_DARKNESS_AT_1X_BASE * 2)
        return radius_4x, darkness, "4x_base"
    if _on_grid(x, step_1x, 0.0) and _on_grid(y, step_1x, page_h):
        return radius_1x, DOT_DARKNESS_AT_1X_BASE, "1x_base"
    if _on_grid(x, step_half, 0.0) and _on_grid(y, step_half, page_h):
        return radius_half, DOT_DARKNESS_AT_1X_BASE, "half_base"
    return radius_quarter, DOT_DARKNESS_AT_1X_BASE, "quarter_base"


def _is_every_third_on_1x_base(
    x: float, y: float, page_h: float, step_1x: float
) -> bool:
    i = round(x / step_1x)
    j = round((page_h - y) / step_1x)
    return i % EVERY_THIRD_ON_1X_BASE == 0 and j % EVERY_THIRD_ON_1X_BASE == 0


def _draw_base_grid(
    c: canvas.Canvas,
    page_w: float,
    page_h: float,
    step_quarter: float,
    step_4x: float,
    step_1x: float,
    step_half: float,
    radius_4x: float,
    radius_1x: float,
    radius_half: float,
    radius_quarter: float,
) -> None:
    for x in _axis_positions_x(page_w, step_quarter):
        for y in _axis_positions_y(page_h, step_quarter):
            radius, darkness, tier = _dot_style(
                x,
                y,
                page_h,
                step_4x,
                step_1x,
                step_half,
                radius_4x,
                radius_1x,
                radius_half,
                radius_quarter,
            )
            if tier == "1x_base" and _is_every_third_on_1x_base(
                x, y, page_h, step_1x
            ):
                c.setFillColorRGB(*COLOR_EVERY_THIRD_ON_1X_BASE)
            else:
                gray = 1 - darkness
                c.setFillColorRGB(gray, gray, gray)
            c.circle(x, y, radius, fill=1, stroke=0)


def _draw_third_base_overlay(
    c: canvas.Canvas,
    page_w: float,
    page_h: float,
    step_third: float,
    radius_third: float,
) -> None:
    c.setFillColorRGB(*COLOR_ON_THIRD_BASE_GRID)
    for x in _axis_positions_x(page_w, step_third):
        for y in _axis_positions_y(page_h, step_third):
            c.circle(x, y, radius_third, fill=1, stroke=0)


def _grid_spacings(base_unit: str) -> dict[str, float]:
    unit = _one_base_unit_points(base_unit)
    return {
        "step_4x": SPACING_4X_BASE * unit,
        "step_1x": SPACING_1X_BASE * unit,
        "step_half": SPACING_HALF_BASE * unit,
        "step_quarter": SPACING_QUARTER_BASE * unit,
        "step_third": SPACING_THIRD_BASE * unit,
    }


def _dot_radii() -> dict[str, float]:
    radius_1x = DOT_RADIUS_1X_MM * mm
    radius_half = radius_1x / 2
    radius_quarter_base = radius_half / 2
    return {
        "radius_4x": radius_1x * DOT_RADIUS_4X_OF_1X,
        "radius_1x": radius_1x,
        "radius_half": radius_half,
        "radius_quarter": radius_half,
        "radius_third": radius_quarter_base * DOT_RADIUS_THIRD_OVERLAY_OF_BASE_QUARTER,
    }


def generate_pdf(base_unit: str, paper: str) -> Path:
    page_w, page_h = _page_size(paper)
    spacings = _grid_spacings(base_unit)
    radii = _dot_radii()
    grid = {**spacings, **radii}
    destination = output_path(base_unit, paper)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(destination), pagesize=(page_w, page_h))

    for _ in range(PAGE_COUNT):
        _draw_base_grid(
            c,
            page_w,
            page_h,
            grid["step_quarter"],
            grid["step_4x"],
            grid["step_1x"],
            grid["step_half"],
            grid["radius_4x"],
            grid["radius_1x"],
            grid["radius_half"],
            grid["radius_quarter"],
        )
        _draw_third_base_overlay(
            c,
            page_w,
            page_h,
            grid["step_third"],
            grid["radius_third"],
        )
        c.showPage()

    c.save()
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate fractional-grid dot paper PDF.")
    parser.add_argument(
        "--base",
        choices=BASE_CHOICES,
        default="cm",
        help="Length of one base grid unit (default: cm)",
    )
    parser.add_argument(
        "--paper",
        choices=PAPER_CHOICES,
        default="letter",
        help="Paper size (default: letter)",
    )
    args = parser.parse_args()

    destination = generate_pdf(args.base, args.paper)
    print(f"Wrote {destination} (base: {args.base}, paper: {args.paper})")


if __name__ == "__main__":
    main()
