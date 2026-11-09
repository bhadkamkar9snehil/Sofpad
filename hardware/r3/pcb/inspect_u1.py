"""Print where the Pro Micro U1 sits on the Sofle RGB reference PCB. Run with KiCad's python:
   "%LOCALAPPDATA%\\Programs\\KiCad\\10.0\\bin\\python.exe" inspect_u1.py
"""
import pcbnew

b = pcbnew.LoadBoard(r"C:\Users\Admin\Documents\Sofpad\hardware\r3\reference\Sofle_RGB\PCB\SofleKeyboard.kicad_pcb")
for fp in b.GetFootprints():
    if fp.GetReference() in ("U1", "J1", "OL1", "OL2", "SW1"):
        pos = fp.GetPosition()
        print(fp.GetReference(), fp.GetFPIDAsString(), "layer", b.GetLayerName(fp.GetLayer()),
              "pos(mm)", round(pcbnew.ToMM(pos.x), 2), round(pcbnew.ToMM(pos.y), 2),
              "rot", fp.GetOrientationDegrees())
fp = b.FindFootprintByReference("U1")
pads = sorted(fp.Pads(), key=lambda p: int(p.GetNumber()) if p.GetNumber().isdigit() else 99)
for p in pads:
    pp = p.GetPosition()
    print(p.GetNumber(), round(pcbnew.ToMM(pp.x), 2), round(pcbnew.ToMM(pp.y), 2), p.GetNetname())
bb = fp.GetBoundingBox()
print("U1 bbox mm", round(pcbnew.ToMM(bb.GetWidth()), 1), round(pcbnew.ToMM(bb.GetHeight()), 1))
