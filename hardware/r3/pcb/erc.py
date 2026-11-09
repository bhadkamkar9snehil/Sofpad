"""Run kicad-cli ERC on a generated schematic and print a summary. Usage: python erc.py carrier"""
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
K = Path(os.environ.get("KICAD_ROOT", r"C:\Users\Admin\AppData\Local\Programs\KiCad\10.0"))


def env():
    e = dict(os.environ)
    e["KICAD10_SYMBOL_DIR"] = str(K / "share" / "kicad" / "symbols")
    e["KICAD10_FOOTPRINT_DIR"] = str(K / "share" / "kicad" / "footprints")
    e["KICAD10_3DMODEL_DIR"] = str(K / "share" / "kicad" / "3dmodels")
    return e


def main(name):
    d = HERE / name
    out = d / "erc.json"
    subprocess.run([str(K / "bin" / "kicad-cli.exe"), "sch", "erc", "--format", "json", "--severity-all",
                    "-o", str(out), str(d / f"{name}.kicad_sch")], env=env(), capture_output=True)
    data = json.loads(out.read_text())
    v = [x for s in data.get("sheets", []) for x in s.get("violations", [])]
    errors = [x for x in v if x["severity"] == "error"]
    print(f"{name} ERC: {len(errors)} errors, {len(v) - len(errors)} warnings", dict(Counter(x["type"] for x in v)))
    for x in errors[:20]:
        print("  ", x["type"], x["description"][:100], [i["description"][:60] for i in x["items"]][:2])
    return len(errors)


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1] if len(sys.argv) > 1 else "carrier") else 0)
