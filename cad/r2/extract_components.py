#!/usr/bin/env python3
"""Extract Sofle RGB switch and encoder positions from its official KiCad PCB.

Run with KiCad's Python interpreter:
  /usr/bin/python3 extract_components.py path/to/SofleKeyboard.kicad_pcb
"""

import json
from pathlib import Path
import sys

import pcbnew


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Pass the source .kicad_pcb file")
    board = pcbnew.LoadBoard(str(Path(sys.argv[1]).resolve()))
    bbox = board.GetBoardEdgesBoundingBox()
    x0 = bbox.GetX()/1e6
    ymax = bbox.GetBottom()/1e6

    def row(f):
        p = f.GetPosition()
        return {
            "ref": f.GetReference(),
            "x": round(p.x/1e6-x0, 4),
            "y": round(ymax-p.y/1e6, 4),
            "angle": round(-f.GetOrientationDegrees(), 2),
        }

    switches = sorted(
        [row(f) for f in board.GetFootprints() if "SK6812MINI_and_cherry" in f.GetFPIDAsString()],
        key=lambda s:int(s["ref"][2:]),
    )
    encoders = [row(f) for f in board.GetFootprints() if "RotaryEncoder" in f.GetFPIDAsString()]
    if len(switches) != 29 or len(encoders) != 1:
        raise ValueError(f"Unexpected components: {len(switches)} keys and {len(encoders)} encoders")

    outdir = Path(__file__).parent
    (outdir / "layout_components.json").write_text(
        json.dumps({"keys":switches,"encoders":encoders},indent=2),encoding="utf-8"
    )
    fmt = lambda a: ",\n".join(f"    [{v['x']}, {v['y']}, {v['angle']}]" for v in a)
    (outdir / "sofle_components.scad").write_text(
        "// Positions copied from the official Sofle RGB KiCad PCB (MIT).\n"
        "// x/y are board-local mm. Angle is corrected for a Y-up view.\n"
        f"key_positions = [\n{fmt(switches)}\n];\n"
        f"encoder_positions = [\n{fmt(encoders)}\n];\n",
        encoding="utf-8",
    )
    print(f"Exported {len(switches)} keys and {len(encoders)} encoder")


if __name__ == "__main__":
    main()
