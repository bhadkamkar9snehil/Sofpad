"""Placement gate: place the carrier without routing and run DRC in seconds. Run with KiCad's python.
Only courtyard, edge and pad-to-pad problems matter here; unconnected items are expected.
Usage: python placecheck.py"""
import drc
import build_pcb
import layouts as L

board, path = build_pcb.build("carrier", "carrier_chk", L.CARRIER_W, L.CARRIER_H, 4, L.CARRIER,
                              L.CARRIER_HOLES, L.CARRIER_KEEPOUT)
import pcbnew
for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
    b = fp.GetBoundingBox(False, False)
    mm = pcbnew.ToMM
    print(f"{fp.GetReference():5} x {mm(b.GetLeft()):5.1f}..{mm(b.GetRight()):5.1f}  y {mm(b.GetTop()):5.1f}..{mm(b.GetBottom()):5.1f}")
bad = drc.main("carrier", "carrier_chk", show=40)
