"""Tidy a routed board: widen tracks under the minimum, drop dangling vias, refill zones.
Run with KiCad's python: python postfix.py carrier carrier"""
import sys
import pcbnew
import drc
from pathlib import Path

folder, name = sys.argv[1], sys.argv[2]
path = Path(__file__).resolve().parent / folder / f"{name}.kicad_pcb"
b = pcbnew.LoadBoard(str(path))
MIN = pcbnew.FromMM(0.15)
widened = 0
for t in b.GetTracks():
    if t.GetClass() == "PCB_TRACK" and t.GetWidth() < MIN:
        t.SetWidth(MIN)
        widened += 1
# a via is dangling when fewer than two track ends or pads touch it
removed = 0
for _ in range(2):
    conn = b.GetConnectivity()
    conn.Build(b)
    for v in [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]:
        items = [i for i in conn.GetConnectedItems(v)
                 if i.m_Uuid != v.m_Uuid]
        layers = {i.GetLayer() for i in items if i.GetClass() == "PCB_TRACK"}
        if len(layers) < 2 and not any(i.GetClass() == "PAD" for i in items):
            b.Remove(v)
            removed += 1
import build_pcb
LAYERS = (pcbnew.B_Cu,) if (len(sys.argv) > 4 and sys.argv[4] == "b") else (pcbnew.F_Cu, pcbnew.B_Cu)
if len(sys.argv) > 3 and sys.argv[3] == "pour":
    # GND pours on both outer layers tie every GND pad and stub to the plane
    bb = b.GetBoardEdgesBoundingBox()
    w, h = pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())
    for layer in LAYERS:
        build_pcb.add_zone(b, layer, b.FindNet("GND"), w, h)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(str(path))
print("widened", widened, "removed vias", removed)
drc.main(folder, name)
