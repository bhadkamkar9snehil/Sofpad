"""Print courtyard sizes of every footprint used by carrier.net.json (KiCad python)."""
import json
import os
import sys

import pcbnew

K = r"C:\Users\Admin\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints"
net = json.load(open(sys.argv[1]))
seen = set()
for ref, p in net["parts"].items():
    if p["fp"] in seen:
        continue
    seen.add(p["fp"])
    lib, name = p["fp"].split(":")
    fp = pcbnew.FootprintLoad(os.path.join(K, lib + ".pretty"), name)
    bb = fp.GetBoundingBox(False)
    cy = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    print(f"{ref:4s} {name[:60]:60s} body {pcbnew.ToMM(bb.GetWidth()):5.1f} x {pcbnew.ToMM(bb.GetHeight()):5.1f}"
          f"  courtyard {pcbnew.ToMM(cy.GetWidth()):5.1f} x {pcbnew.ToMM(cy.GetHeight()):5.1f}")
