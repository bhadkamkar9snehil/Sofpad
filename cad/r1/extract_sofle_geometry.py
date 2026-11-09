#!/usr/bin/env python3
"""Convert the official Sofle RGB KiCad board outline to OpenSCAD parameters.

Run with KiCad 9's system Python:
    /usr/bin/python3 extract_sofle_geometry.py PATH/TO/SofleKeyboard.kicad_pcb

The output is written beside this script as sofle_rgb_geometry.scad.
"""

from __future__ import annotations

import pathlib
import sys

import pcbnew


SOURCE_COMMIT = "fb294f7c58d0f91c379a9ef339159d4d056643e9"


def point_xy(vec, x_min_mm: float, y_max_mm: float) -> tuple[float, float]:
    return (
        round(vec.x / 1_000_000 - x_min_mm, 4),
        round(y_max_mm - vec.y / 1_000_000, 4),
    )


def to_scad_array(values: list[tuple[float, float]]) -> str:
    return "[\n" + ",\n".join(f"    [{x:.4f}, {y:.4f}]" for x, y in values) + "\n]"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: extract_sofle_geometry.py path/to/SofleKeyboard.kicad_pcb")

    source = pathlib.Path(sys.argv[1]).resolve()
    board = pcbnew.LoadBoard(str(source))
    bbox = board.GetBoardEdgesBoundingBox()
    x0 = bbox.GetX() / 1_000_000
    y_max = bbox.GetBottom() / 1_000_000
    width = bbox.GetWidth() / 1_000_000
    height = bbox.GetHeight() / 1_000_000

    contours = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(contours):
        raise ValueError("KiCad cannot close the PCB edge contour")
    if contours.OutlineCount() != 1:
        raise ValueError(f"Expected one PCB perimeter; got {contours.OutlineCount()}")

    outline = contours.COutline(0)
    vertices = [point_xy(outline.CPoint(i), x0, y_max) for i in range(outline.PointCount())]

    holes = [
        (footprint.GetReference(), point_xy(footprint.GetPosition(), x0, y_max))
        for footprint in board.GetFootprints()
        if "HOLE_M2" in footprint.GetFPIDAsString().upper()
        or "M2_HOLE" in footprint.GetFPIDAsString().upper()
    ]
    holes.sort(key=lambda h: h[0])
    if len(holes) != 7:
        raise ValueError(f"Expected seven M2 mounting holes; got {len(holes)}")

    trrs = [
        point_xy(f.GetPosition(), x0, y_max)
        for f in board.GetFootprints()
        if "MJ-4PP" in f.GetFPIDAsString().upper()
    ]
    if len(trrs) != 1:
        raise ValueError(f"Expected one TRRS connector; got {len(trrs)}")

    result = f'''// Generated from Sofle RGB PCB by extract_sofle_geometry.py.
// Source: https://github.com/josefadamcik/SofleKeyboard
// Git commit: {SOURCE_COMMIT}
// The source project is MIT licensed; see LICENSE-SOFLE.txt.
// Units: mm. Origin: board bounding box, lower-left in the OpenSCAD view.
// The RIGHT half uses this outline. The LEFT half is mirrored in X.

board_w = {width:.4f};
board_h = {height:.4f};
board_outline = {to_scad_array(vertices)};
board_mount_holes = {to_scad_array([coordinates for _, coordinates in holes])};
board_trrs = [{trrs[0][0]:.4f}, {trrs[0][1]:.4f}];
'''
    dest = pathlib.Path(__file__).with_name("sofle_rgb_geometry.scad")
    dest.write_text(result, encoding="utf-8")
    print(f"Saved {dest} with {len(vertices)} outline vertices and {len(holes)} M2 holes")


if __name__ == "__main__":
    main()
