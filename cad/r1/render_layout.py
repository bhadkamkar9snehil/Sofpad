#!/usr/bin/env python3
"""Draw the default PCB + trackpad case plan from extracted Sofle dimensions.

This engineering plan shows placement only. The SCAD model is the source of
truth for all case heights, pockets, cable slots, and the printable solid.
"""

from __future__ import annotations

import json
import pathlib
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle


ROOT = pathlib.Path(__file__).parent
SCAD = (ROOT / "sofle_rgb_geometry.scad").read_text(encoding="utf-8")


def num(name: str) -> float:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*([0-9.]+)\s*;", SCAD)
    if not match:
        raise ValueError(name)
    return float(match.group(1))


def array(name: str) -> list[list[float]]:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*(\[[^;]+\])\s*;", SCAD)
    if not match:
        raise ValueError(name)
    return json.loads(match.group(1))


def main() -> None:
    board_w, board_h = num("board_w"), num("board_h")
    outline = array("board_outline")
    holes = array("board_mount_holes")
    trrs = array("board_trrs")

    gap, side, end, pad_zone_w = 17.0, 10.0, 12.0, 66.0
    case_w, case_h = 2 * board_w + gap + pad_zone_w + 2 * side, board_h + 2 * end
    left_x = side
    right_x = side + board_w + gap
    pad_zone_x = right_x + board_w
    pad_cx = pad_zone_x + pad_zone_w / 2
    pad_cy = case_h / 2

    fig, ax = plt.subplots(figsize=(16.5, 7.1))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    ax.add_patch(FancyBboxPatch((0, 0), case_w, case_h,
                                boxstyle="round,pad=0,rounding_size=11",
                                linewidth=2.0, edgecolor="#303b46", facecolor="#f0f2f3"))

    for side_name, bx, mirrored in (("LEFT", left_x, True), ("RIGHT", right_x, False)):
        def transform(pt: list[float]) -> tuple[float, float]:
            return (bx + (board_w - pt[0] if mirrored else pt[0]), end + pt[1])

        board = [transform(pt) for pt in outline]
        ax.add_patch(Polygon(board, closed=True, facecolor="#b8ded0",
                             edgecolor="#1f7660", linewidth=1.5, alpha=0.96))
        for pt in holes:
            ax.add_patch(Circle(transform(pt), radius=1.15,
                                facecolor="white", edgecolor="#165b4b", linewidth=1.2))
        tpos = transform(trrs)
        ax.add_patch(Circle(tpos, 2.4, facecolor="#dc8141", edgecolor="#85451b"))
        ax.annotate("TRRS", (tpos[0],tpos[1]), (tpos[0],tpos[1]+15),
                    ha="center", fontsize=8, color="#985524",
                    arrowprops={"arrowstyle":"->","color":"#985524","lw":0.9})
        ax.text(bx + board_w / 2, 14, f"{side_name} · seven M2 points",
                ha="center", va="center", fontsize=10, color="#174f42")

    ax.add_patch(FancyBboxPatch((pad_cx-22.1, pad_cy-20.6),44.2,41.2,
                                boxstyle="round,pad=0,rounding_size=1.2",
                                facecolor="#343f4d", edgecolor="#222d37", linewidth=1.2))
    ax.text(pad_cx,pad_cy,"TPS43\n43 × 40 mm",ha="center",va="center",
            color="white",fontsize=10,linespacing=1.4)
    ax.text(pad_cx,case_h-11,"TRACKPAD",ha="center",fontsize=10,color="#303b46")

    ax.annotate("",xy=(0,-7),xytext=(case_w,-7),
                arrowprops={"arrowstyle":"|-|","color":"#4f5c68"})
    ax.text(case_w/2,-12,f"{case_w:.1f} mm · one-piece body",ha="center",
            va="top",fontsize=10,color="#4f5c68")

    ax.annotate("",xy=(case_w+7,0),xytext=(case_w+7,case_h),
                arrowprops={"arrowstyle":"|-|","color":"#4f5c68"})
    ax.text(case_w+12,case_h/2,f"{case_h:.1f} mm",rotation=90,
            ha="center",va="center",fontsize=10,color="#4f5c68")

    ax.set_xlim(-17,case_w+25)
    ax.set_ylim(-27,case_h+14)
    ax.set_aspect("equal",adjustable="box")
    ax.axis("off")
    ax.set_title("Sofle RGB · couch case · default top-down layout",
                 fontsize=16,loc="left",color="#222b36",pad=10)
    ax.text(0,-24,"PCB outline and hole coordinates: official Sofle RGB KiCad (MIT). "
            "Verify against your physical revision before printing.",
            fontsize=8,ha="left",color="#66727d")
    fig.tight_layout(pad=0.6)
    for ext in ("svg", "png"):
        fig.savefig(ROOT / f"CAD_layout.{ext}",dpi=180,facecolor="white")
    plt.close(fig)
    print(f"Wrote CAD_layout.svg and CAD_layout.png ({case_w:.1f} × {case_h:.1f} mm)")


if __name__ == "__main__":
    main()
