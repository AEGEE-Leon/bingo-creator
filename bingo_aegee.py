#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import io
import random
import argparse
from pathlib import Path
import copy

from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics

from pypdf import PdfReader, PdfWriter


# ---------------- CSV ----------------
def read_first_column(csv_path: Path) -> list[str]:
    items: list[str] = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            text = (row[0] or "").strip()
            if text:
                items.append(text)

    # De-duplicate preserving order
    seen = set()
    deduped: list[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            deduped.append(x)
    return deduped


# ---------------- Bingo grid ----------------
def make_grid(items: list[str], rng: random.Random, center_mode: str, free_text: str):
    needed = 24  # keep center reserved
    if len(items) < needed:
        raise ValueError(f"Need at least {needed} distinct items, got {len(items)}.")

    chosen = rng.sample(items, needed)

    grid: list[list[str | None]] = [[None] * 5 for _ in range(5)]
    idx = 0
    for r in range(5):
        for c in range(5):
            if r == 2 and c == 2:
                grid[r][c] = free_text if center_mode == "free" else None
            else:
                grid[r][c] = chosen[idx]
                idx += 1
    return grid


# ---------------- Text wrapping ----------------
def wrap_text(
    text: str,
    max_width: float,
    font_name: str,
    font_size: int,
    max_lines: int = 6,
) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = ""

    for w in words:
        test = (current + " " + w).strip()
        if stringWidth(test, font_name, font_size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
            if len(lines) >= max_lines:
                break

    if len(lines) < max_lines and current:
        lines.append(current)

    # Ellipsis-trim last line if still too wide
    if lines:
        last = lines[-1]
        while stringWidth(last, font_name, font_size) > max_width and len(last) > 1:
            last = last[:-2] + "…"
        lines[-1] = last

    return lines[:max_lines]


# ---------------- Overlay page (text only) ----------------
def make_overlay_page_pdf(
    page_w: float,
    page_h: float,
    grid: list[list[str | None]],
    center_mode: str,
    # margins are fractions of the page (0..1)
    m_left: float,
    m_right: float,
    m_top: float,
    m_bottom: float,
    # text
    font_name: str,
    font_size: int,
    # padding
    padding_pt: float,
):
    """
    Creates a 1-page PDF (in memory) with ONLY the bingo text drawn over a 5x5 area.
    Text is centered horizontally and vertically within each cell, with configurable padding.
    Margins define the table rectangle; it is then divided by 5x5 to get the cells.
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_w, page_h))
    c.setFont(font_name, font_size)

    # Table rectangle derived from margins
    left_x = page_w * m_left
    right_x = page_w * (1.0 - m_right)
    top_y = page_h * (1.0 - m_top)
    bottom_y = page_h * m_bottom

    if right_x <= left_x or top_y <= bottom_y:
        raise ValueError("Margins produce an invalid table area. Check --m-left/right/top/bottom.")

    table_w = right_x - left_x
    table_h = top_y - bottom_y

    cell_w = table_w / 5.0
    cell_h = table_h / 5.0

    # Font metrics for true vertical centering
    ascent = pdfmetrics.getAscent(font_name, font_size)    # positive
    descent = pdfmetrics.getDescent(font_name, font_size)  # negative
    line_h = ascent - descent
    gap = line_h * 0.10  # extra gap between lines

    for r in range(5):          # r=0 is top row
        for col in range(5):
            if r == 2 and col == 2 and center_mode == "keep":
                continue

            text = grid[r][col]
            if text is None:
                continue

            # Cell bounds in PDF coords
            cell_left = left_x + col * cell_w
            cell_bottom = top_y - (r + 1) * cell_h

            usable_w = cell_w - 2 * padding_pt
            if usable_w <= 1:
                usable_w = cell_w * 0.5  # fallback

            lines = wrap_text(text, usable_w, font_name, font_size, max_lines=6)

            total_h = (len(lines) * line_h) + ((len(lines) - 1) * gap) if lines else line_h

            # True vertical centering for the whole block
            block_top = cell_bottom + (cell_h + total_h) / 2
            first_baseline = block_top - ascent

            for i, line in enumerate(lines):
                y = first_baseline - i * (line_h + gap)
                c.drawCentredString(cell_left + cell_w / 2, y, line)

    c.showPage()
    c.save()
    buf.seek(0)
    return buf


# ---------------- Main export ----------------
def export_bingos_pdf_from_pdf_template(
    template_pdf: Path,
    csv_path: Path,
    out_pdf: Path,
    n: int,
    seed: int | None,
    center_mode: str,
    free_text: str,
    # margins
    m_left: float,
    m_right: float,
    m_top: float,
    m_bottom: float,
    # text
    font_name: str,
    font_size: int,
    # padding
    padding_pt: float,
):
    if not template_pdf.exists():
        raise FileNotFoundError(f"Template PDF not found: {template_pdf}")
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    items = read_first_column(csv_path)
    rng = random.Random(seed)

    reader = PdfReader(str(template_pdf))
    if not reader.pages:
        raise ValueError("Template PDF has no pages.")

    template_page = reader.pages[0]
    page_w = float(template_page.mediabox.width)
    page_h = float(template_page.mediabox.height)

    writer = PdfWriter()

    for _ in range(n):
        grid = make_grid(items, rng, center_mode, free_text)

        overlay_buf = make_overlay_page_pdf(
            page_w=page_w,
            page_h=page_h,
            grid=grid,
            center_mode=center_mode,
            m_left=m_left,
            m_right=m_right,
            m_top=m_top,
            m_bottom=m_bottom,
            font_name=font_name,
            font_size=font_size,
            padding_pt=padding_pt,
        )
        overlay_reader = PdfReader(overlay_buf)
        overlay_page = overlay_reader.pages[0]

        page = copy.copy(template_page)
        page.merge_page(overlay_page)
        writer.add_page(page)

    with out_pdf.open("wb") as f:
        writer.write(f)


def main():
    parser = argparse.ArgumentParser(
        description="Generate N bingo pages as a PDF using a PDF template as the background."
    )
    parser.add_argument("--template-pdf", default="aegeeleon-bingo-template.pdf", help="Background template PDF")
    parser.add_argument("--csv", default="puntos.csv", help="CSV file with items in the first column")
    parser.add_argument("-n", "--number", type=int, default=1, help="Number of bingo pages to generate")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (optional)")
    parser.add_argument("--out", default="bingos_aegee_leon.pdf", help="Output PDF path")

    parser.add_argument(
        "--center",
        choices=["keep", "free"],
        default="keep",
        help="Center cell behavior: keep (leave template untouched) or free (write text)",
    )
    parser.add_argument("--free-text", default="FREE", help="Text to write in the center cell when --center free")

    # Margins as page fractions (0..1)
    parser.add_argument("--m-left", type=float, default=0.10, help="Left margin (fraction of page width)")
    parser.add_argument("--m-right", type=float, default=0.10, help="Right margin (fraction of page width)")
    parser.add_argument("--m-top", type=float, default=0.245, help="Top margin (fraction of page height)")
    parser.add_argument("--m-bottom", type=float, default=0.115, help="Bottom margin (fraction of page height)")

    parser.add_argument("--font-name", default="Helvetica", help="Font name (ReportLab built-in fonts recommended)")
    parser.add_argument("--font-size", type=int, default=9, help="Font size in points")

    # Padding in points (NOT a fraction)
    parser.add_argument("--padding", type=float, default=6.0, help="Cell padding in points")

    args = parser.parse_args()

    export_bingos_pdf_from_pdf_template(
        template_pdf=Path(args.template_pdf),
        csv_path=Path(args.csv),
        out_pdf=Path(args.out),
        n=args.number,
        seed=args.seed,
        center_mode=args.center,
        free_text=args.free_text,
        m_left=args.m_left,
        m_right=args.m_right,
        m_top=args.m_top,
        m_bottom=args.m_bottom,
        font_name=args.font_name,
        font_size=args.font_size,
        padding_pt=args.padding,
    )

    print(f"✔ PDF created: {args.out} ({args.number} pages)")


if __name__ == "__main__":
    main()
