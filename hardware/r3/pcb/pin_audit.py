"""Print every pin of the chosen ICs and connectors as: pin  library function name  net,
so each can be compared with the datasheet. Run: python pin_audit.py U2 U3 ..."""
import json
import sys
from pathlib import Path
import kilib

HERE = Path(__file__).resolve().parent
net = json.loads((HERE / "carrier" / "carrier.net.json").read_text())
pin_net = {}
for n, pins in net["nets"].items():
    for p in pins:
        pin_net[p] = n
for ref in sys.argv[1:]:
    part = net["parts"][ref]
    lib, sym = part["sym"].split(":")
    sp = {num: nm for num, nm, *_ in kilib.symbol_pins(lib, sym)} if ref != "U3" else None
    if sp is None:
        sp = {num: nm for num, nm, *_ in kilib.symbol_pins("sofpad", sym)} if False else {}
    print(f"--- {ref} {part['value']} ({part['sym']})")
    nums = sorted({k.split(".", 1)[1] for k in pin_net if k.startswith(ref + ".")}, key=lambda s: (len(s), s))
    print("   ", "  ".join(f"{n}:{(sp.get(n) or '?')}={pin_net[f'{ref}.{n}']}" for n in nums))
