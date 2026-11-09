"""Run kicad-cli DRC on a board and print a summary. Usage: python drc.py carrier carrier  (folder, board)"""
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
K = Path(os.environ.get("KICAD_ROOT", r"C:\Users\Admin\AppData\Local\Programs\KiCad\10.0"))


def main(folder, board, show=14):
    e = dict(os.environ)
    e["KICAD10_FOOTPRINT_DIR"] = str(K / "share" / "kicad" / "footprints")
    e["KICAD10_3DMODEL_DIR"] = str(K / "share" / "kicad" / "3dmodels")
    pcb = HERE / folder / f"{board}.kicad_pcb"
    out = HERE / folder / f"{board}.drc.json"
    subprocess.run([str(K / "bin" / "kicad-cli.exe"), "pcb", "drc", "--format", "json", "--severity-all",
                    "--all-track-errors", "-o", str(out), str(pcb)], env=e, capture_output=True)
    d = json.loads(out.read_text())
    v = d["violations"]
    u = d.get("unconnected_items", [])
    errs = [x for x in v if x["severity"] == "error"]
    print(f"{board}: {len(errs)} errors, {len(v) - len(errs)} warnings, {len(u)} unconnected",
          dict(Counter(x["type"] for x in v)))
    for x in errs[:show]:
        print("  ", x["type"], x["description"][:80], [i["description"][:48] for i in x["items"]][:2])
    for x in u[:6]:
        print("   unconnected:", [i["description"][:60] for i in x["items"]][:2])
    return len(errs) + len(u)


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1], sys.argv[2]) else 0)
