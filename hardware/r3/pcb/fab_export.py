"""Export fabrication files for a board: Gerbers, drill, pick-and-place and a BOM grouped by value.
Usage: python fab_export.py carrier carrier     (folder, board)    -> fab/<board>/ and fab/<board>.zip
Order form settings are in ARCHITECTURE.md (Manufacturing)."""
import csv
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
K = Path(os.environ.get("KICAD_ROOT", r"C:\Users\Admin\AppData\Local\Programs\KiCad\10.0"))
CLI = str(K / "bin" / "kicad-cli.exe")


def run(args):
    e = dict(os.environ, KICAD10_FOOTPRINT_DIR=str(K / "share" / "kicad" / "footprints"))
    r = subprocess.run([CLI] + args, env=e, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stdout + r.stderr)


def main(folder, board):
    pcb = HERE / folder / f"{board}.kicad_pcb"
    out = HERE / "fab" / board
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    run(["pcb", "export", "gerbers", "-o", str(out), str(pcb)])
    run(["pcb", "export", "drill", "--format", "excellon", "-o", str(out) + os.sep, str(pcb)])
    pos = out / f"{board}-pos.csv"
    run(["pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "-o", str(pos), str(pcb)])
    net = json.loads((HERE / folder / f"{folder}.net.json").read_text())
    groups = defaultdict(list)
    for ref, p in net["parts"].items():
        groups[(p["value"], p["fp"].split(":")[1])].append(ref)
    with open(out / f"{board}-bom.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "Quantity"])
        for (val, fp), refs in sorted(groups.items()):
            w.writerow([val, ",".join(sorted(refs)), fp, len(refs)])
    zipbase = HERE / "fab" / board
    shutil.make_archive(str(zipbase), "zip", out)
    print("wrote", out, "and", f"{zipbase}.zip", len(list(out.iterdir())), "files")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
