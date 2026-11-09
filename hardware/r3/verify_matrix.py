#!/usr/bin/env python3
"""Extract and validate the original Josef Adamcik Sofle RGB matrix.

Run using the KiCad system Python: /usr/bin/python3 verify_matrix.py
The output is source-derived JSON, not an assumed keyboard layout.
"""
import json
from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "reference/Sofle_RGB/PCB/SofleKeyboard.kicad_pcb"
TARGET = ROOT / "source_pinmap.json"

pcb = pcbnew.LoadBoard(str(SOURCE))
parts = {fp.GetReference(): fp for fp in pcb.GetFootprints()}


def pads(ref):
    # A reversible PCB can have overlapping front/back duplicate pad numbers.
    result = {}
    for pad in parts[ref].Pads():
        num = pad.GetNumber()
        net = pad.GetNetname()
        if num in result and result[num] != net:
            raise ValueError(f"Inconsistent duplicate pad {ref}.{num}")
        result[num] = net
    return result


rows = [f"row{i}" for i in range(5)]
cols = [f"col{i}" for i in range(5)] + ["SW25A"]
u1 = pads("U1")
diode_by_anode_net = {}
for number in range(1, 31):
    ref = f"D{number}"
    diode = pads(ref)
    if diode["1"] not in rows:
        raise ValueError(f"Unexpected row for {ref}: {diode}")
    diode_by_anode_net[diode["2"]] = diode["1"]

keys = []
for number in range(1, 31):
    ref = f"SW{number}"
    switch = pads(ref)
    if number == 25:
        diode_net, column = switch["S2"], switch["S1"]
    else:
        diode_net, column = switch["5"], switch["6"]
    row = diode_by_anode_net[diode_net]
    if column not in cols:
        raise ValueError(f"Unexpected column for {ref}: {column}")
    keys.append({"switch": ref, "row": row, "col": column,
                 "diode_net": diode_net})

addresses = {(k["row"], k["col"]) for k in keys}
assert len(keys) == 30, len(keys)
assert len(addresses) == 30, f"Matrix short or collision: {len(addresses)}"
assert {key["row"] for key in keys} == set(rows)
assert {key["col"] for key in keys} == set(cols)

expected = {
    "8": "row0", "9": "row1", "10": "row2", "11": "row3",
    "12": "row4", "13": "SW25A", "14": "col4", "15": "col3",
    "16": "col2", "17": "col1", "18": "col0",
    "19": "ENCB", "20": "ENCA", "5": "SDA", "6": "SCL"
}
for pin, net in expected.items():
    assert u1[pin] == net, (pin, net, u1[pin])

result = {
    "origin": "Josef Adamcik Sofle RGB KiCad PCB, commit fb294f7c58d0f91c379a9ef339159d4d056643e9",
    "board": str(SOURCE.relative_to(ROOT)),
    "matrix": {"rows": rows, "columns": cols, "switches": 30,
               "note": "SW25 is encoder push-button and is included"},
    "promicro_pad_to_net": {str(n): u1[str(n)] for n in range(1,25)},
    "keys": keys,
    "verified": {"all_30_positions_unique": True,
                 "five_rows_six_columns": True,
                 "encoders_A_B_at_20_19": True}
}
TARGET.write_text(json.dumps(result, indent=2) + "\n")
print(f"PASS 30 unique matrix positions, 5 rows × 6 columns")
print("U1 Pro Micro pads: 8–12 rows, 13–18 columns, 19–20 encoder A/B")
print("Wrote", TARGET)
