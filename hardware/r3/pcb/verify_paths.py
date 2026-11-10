"""End-to-end signal check, no hardware: every Sofle Pro Micro pad -> adapter header -> adapter FFC pin
-> carrier FFC pin -> carrier net -> nRF52840 module pad -> GPIO name, compared with the allocation
table in ARCHITECTURE.md. Assumes a straight cable (pin k to pin k). Run: python verify_paths.py"""
import json
from pathlib import Path
import kilib

HERE = Path(__file__).resolve().parent
src = json.loads((HERE.parent / "source_pinmap.json").read_text())
ad = json.loads((HERE / "adapter" / "adapter.net.json").read_text())["nets"]
car = json.loads((HERE / "carrier" / "carrier.net.json").read_text())["nets"]
pins = {n: nm for n, nm, *_ in kilib.symbol_pins("RF_Module", "MDBT50Q-1MV2")}

EXPECT = {  # carrier net -> nRF GPIO, from ARCHITECTURE.md
    **{f"ROW{i}": f"P0.{13 + i}" for i in range(5)},
    **{f"RIGHT_COL{i}": f"P0.{19 + i}" for i in range(6)},
    "LEFT_COL0": "P0.25", "LEFT_COL1": "P0.26", "LEFT_COL2": "P0.27",
    "LEFT_COL3": "P1.00", "LEFT_COL4": "P1.01", "LEFT_COL5": "P1.02",
    "LEFT_ENC_A": "P1.03", "LEFT_ENC_B": "P1.04", "RIGHT_ENC_A": "P1.05", "RIGHT_ENC_B": "P1.06",
    "SDA": "P0.04", "SCL": "P0.05", "TP_RDY": "P0.06", "TP_NRST": "P0.07", "ACC_INT": "P0.08",
}
bad = 0


def find(nets, pin):
    return next((n for n, p in nets.items() if pin in p), None)


def carrier_net(conn, pin):
    return find(car, f"{conn}.{pin}")


for half, conn in (("left", "J7"), ("right", "J8")):
    print(f"== {half} half: Sofle -> adapter -> {conn}")
    for pad, sig in sorted(src["promicro_pad_to_net"].items(), key=lambda kv: int(kv[0])):
        if not (sig.startswith(("row", "col")) or sig in ("SW25A", "ENCA", "ENCB")):
            continue
        hdr = f"HL.{pad}" if int(pad) <= 12 else f"HR.{25 - int(pad)}"
        anet = find(ad, hdr)
        ffc = next((p for p in ad[anet] if p.startswith("J1.")), None) if anet else None
        pin = ffc.split(".")[1] if ffc else None
        cnet = carrier_net(conn, pin) if pin else None
        # expected carrier net for this signal
        if sig.startswith("row"):
            want = "ROW" + sig[3:]
        elif sig == "SW25A":
            want = f"{half.upper()}_COL5"
        elif sig.startswith("col"):
            want = f"{half.upper()}_COL{sig[3:]}"
        else:
            want = f"{half.upper()}_ENC_{'A' if sig == 'ENCA' else 'B'}"
        u1 = next((p.split('.')[1] for p in car.get(cnet, []) if p.startswith("U1.")), None) if cnet else None
        gpio = pins.get(u1)
        ok = cnet == want and gpio == EXPECT.get(want)
        bad += not ok
        print(f"  {'ok ' if ok else 'BAD'} pad {pad:>2} {sig:5} {hdr:6} FFC{pin:>3} -> {cnet} -> U1.{u1} {gpio}")
    g = [p for p in ad["GND"] if p.startswith("J1.")]
    gc = carrier_net(conn, g[0].split(".")[1])
    print(f"  {'ok ' if gc == 'GND' else 'BAD'} GND FFC {g} -> {gc}")
    bad += gc != "GND"

print("== other carrier nets: module pad -> GPIO")
for net, want in EXPECT.items():
    u1 = next((p.split('.')[1] for p in car[net] if p.startswith("U1.")), None)
    ok = pins.get(u1) == want
    bad += not ok
    if not ok:
        print("  BAD", net, u1, pins.get(u1), "want", want)
for net in ("USB_DP", "USB_DM", "VBUS", "SWDIO", "SWDCLK", "RESET", "LCD_MOSI", "LCD_SCK", "LCD_CS", "LCD_DC", "LCD_RST", "LCD_BL", "HAPTIC_EN", "CHG", "PGOOD", "VBAT_SENSE"):
    u1 = next((p.split('.')[1] for p in car[net] if p.startswith("U1.")), None)
    print(f"  {net:11} U1.{u1} = {pins.get(u1)}")
print("FAIL" if bad else "PASS", bad, "problems")
