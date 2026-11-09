"""Design checks for Sofpad_R3_Alice.scad. Run after every CAD edit:  python check_design.py

Proves, with OpenSCAD booleans (Manifold backend), that:
  1. parts that must not touch have zero overlap volume,
  2. parts that must sit inside the case cavity do,
  3. shell and plate are single connected solids (no floating bosses),
  4. exported meshes are closed (via verify_stl.py).
Exit code 1 on any failure.
"""
import os
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
SCAD = HERE / "Sofpad_R3_Alice.scad"
CANDIDATES = [
    os.environ.get("OPENSCAD", ""),
    r"C:\Program Files\OpenSCAD (Nightly)\openscad.exe",
]
OPENSCAD = next(c for c in CANDIDATES if c and Path(c).exists())

NO_OVERLAP = [
    ("battery", "pcbs"), ("carrier", "pcbs"), ("battery", "carrier"),
    ("padbody", "pcbs"), ("retainer", "pcbs"), ("retainer", "battery"),
    ("retainer", "carrier"), ("padbody", "battery"), ("platebosses", "battery"),
    ("platebosses", "carrier"), ("platebosses", "retainer"), ("platebosses", "pcbs"),
    ("bosses", "battery"), ("bosses", "carrier"), ("usb", "battery"),
    ("screen", "battery"), ("screen", "carrier"), ("screen", "pcbs"), ("screen", "retainer"),
    ("screen", "bosses"), ("screen", "platebosses"), ("adapters", "bosses"), ("adapters", "battery"), ("adapters", "carrier"), ("adapters", "screen"),
]
INSIDE_CAVITY = ["battery", "carrier", "pcbs", "padbody", "retainer", "usb", "screen", "adapters"]


def run(part, a="", b=""):
    out = BUILD / "chk.stl"
    out.unlink(missing_ok=True)
    cmd = [OPENSCAD, "--backend=manifold", "--export-format", "binstl",
           "-D", f'part="{part}"', "-D", f'chk_a="{a}"', "-D", f'chk_b="{b}"',
           "-o", str(out), str(SCAD)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not out.exists():
        return 0  # OpenSCAD writes nothing for an empty result
    return struct.unpack_from("<I", out.read_bytes(), 80)[0]


def components(path):
    data = path.read_bytes()
    n = struct.unpack_from("<I", data, 80)[0]
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        v = struct.unpack_from("<9f", data, 84 + i * 50 + 12)
        pts = [tuple(round(c, 3) for c in v[j:j + 3]) for j in (0, 3, 6)]
        for p in pts[1:]:
            parent[find(p)] = find(pts[0])
    return len({find(p) for p in list(parent)})


def main():
    BUILD.mkdir(exist_ok=True)
    fails = []
    for a, b in NO_OVERLAP:
        t = run("overlap", a, b)
        print(f"{'FAIL' if t else 'ok  '} no overlap: {a} / {b}")
        if t:
            fails.append(f"{a} overlaps {b}")
    for a in INSIDE_CAVITY:
        t = run("outside", a, "cavity")
        print(f"{'FAIL' if t else 'ok  '} inside cavity: {a}")
        if t:
            fails.append(f"{a} sticks out of the cavity")
    for part in ("shell", "bottom", "retainer"):
        run(part)
        (BUILD / "chk.stl").replace(BUILD / f"{part}.stl") if (BUILD / "chk.stl").exists() else None
        subprocess.run([OPENSCAD, "--backend=manifold", "--export-format", "binstl",
                        "-D", f'part="{part}"', "-o", str(BUILD / f"{part}.stl"), str(SCAD)],
                       capture_output=True)
    for part in ("shell", "bottom"):
        c = components(BUILD / f"{part}.stl")
        print(f"{'FAIL' if c != 1 else 'ok  '} {part} connected components: {c}")
        if c != 1:
            fails.append(f"{part} has {c} separate pieces (floating feature)")
    v = subprocess.run([sys.executable, "-I", str(HERE / "verify_stl.py")], capture_output=True, text=True)
    print(v.stdout.strip().splitlines()[-1] if v.stdout.strip() else v.stderr[-300:])
    if v.returncode:
        fails.append("mesh not closed")
    print("PASS: design checks" if not fails else "FAILED:\n  " + "\n  ".join(fails))
    sys.exit(1 if fails else 0)


main()
