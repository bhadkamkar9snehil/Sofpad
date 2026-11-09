"""List parts near the Pro Micro position on the Sofle RGB reference PCB (KiCad python)."""
import pcbnew

b = pcbnew.LoadBoard(r"C:\Users\Admin\Documents\Sofpad\hardware\r3\reference\Sofle_RGB\PCB\SofleKeyboard.kicad_pcb")
u1 = b.FindFootprintByReference("U1")
bb = u1.GetBoundingBox(False)
x0, y0, x1, y1 = [pcbnew.ToMM(v) for v in (bb.GetX(), bb.GetY(), bb.GetRight(), bb.GetBottom())]
print("U1 bbox", round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1))
for fp in b.GetFootprints():
    r = fp.GetReference()
    if r == "U1":
        continue
    fb = fp.GetBoundingBox(False)
    fx0, fy0, fx1, fy1 = [pcbnew.ToMM(v) for v in (fb.GetX(), fb.GetY(), fb.GetRight(), fb.GetBottom())]
    if fx1 > x0 - 12 and fx0 < x1 + 12 and fy1 > y0 - 14 and fy0 < y1 + 14:
        print(r, fp.GetFPIDAsString()[:40], "layer", b.GetLayerName(fp.GetLayer()), [round(v, 1) for v in (fx0, fy0, fx1, fy1)])
edge = b.GetBoardEdgesBoundingBox()
print("board edge bbox", [round(pcbnew.ToMM(v), 1) for v in (edge.GetX(), edge.GetY(), edge.GetRight(), edge.GetBottom())])
