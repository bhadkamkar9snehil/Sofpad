"""Independent netlist cross-check. For a board, compare three sources of connectivity:
  1. the generator's net.json (what the design intends),
  2. the netlist KiCad itself derives from the saved schematic (kicad-cli),
  3. the pad nets stored in the routed PCB.
Run with KiCad's python: python compare_nets.py carrier carrier [pcb_name]"""
import json
import os
import subprocess
import sys
from pathlib import Path
import kilib

HERE = Path(__file__).resolve().parent
K = Path(os.environ.get("KICAD_ROOT", r"C:\Users\Admin\AppData\Local\Programs\KiCad\10.0"))
folder, sch_name = sys.argv[1], sys.argv[2]
pcb_name = sys.argv[3] if len(sys.argv) > 3 else sch_name
d = HERE / folder
intended = json.loads((d / f"{folder}.net.json").read_text())["nets"]


def groups(nets):
    return {frozenset(pins) for pins in nets.values() if len(pins) > 1}


A = groups(intended)

# 2. KiCad netlist from the schematic
out = d / "check.net"
env = dict(os.environ, KICAD10_SYMBOL_DIR=str(K / "share/kicad/symbols"), KICAD10_FOOTPRINT_DIR=str(K / "share/kicad/footprints"))
r = subprocess.run([str(K / "bin/kicad-cli.exe"), "sch", "export", "netlist", "--format", "kicadsexpr", "-o", str(out),
                    str(d / f"{sch_name}.kicad_sch")], env=env, capture_output=True, text=True)
tree = kilib.parse(out.read_text(encoding="utf-8"))
nets = next(c for c in tree if isinstance(c, list) and c and c[0] == "nets")
B = set()
for n in nets[1:]:
    nodes = [f"{next(c for c in x if c[0] == 'ref')[1]}.{next(c for c in x if c[0] == 'pin')[1]}"
             for x in n if isinstance(x, list) and x[0] == "node"]
    if len(nodes) > 1:
        B.add(frozenset(nodes))

# 3. PCB pad nets
import pcbnew
board = pcbnew.LoadBoard(str(d / f"{pcb_name}.kicad_pcb"))
byname = {}
for fp in board.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname():
            byname.setdefault(pad.GetNetname(), set()).add(f"{fp.GetReference()}.{pad.GetNumber()}")
C = {frozenset(v) for v in byname.values() if len(v) > 1}


def report(label, X):
    only_a = A - X
    only_x = X - A
    print(f"{label}: {'MATCH' if not only_a and not only_x else 'DIFF'}  intended nets {len(A)}, other {len(X)}")
    for s in list(only_a)[:6]:
        print("   intended only:", sorted(s)[:8])
    for s in list(only_x)[:6]:
        print("   other only:   ", sorted(s)[:8])
    return not only_a and not only_x


ok = report("schematic (KiCad netlist)", B)
ok &= report("routed PCB pads", C)
print("PASS" if ok else "FAIL")
