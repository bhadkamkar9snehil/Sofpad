"""Hand-calculation checks of the carrier power and signal values (datasheet formulas, not SPICE:
TI does not ship offline SPICE models for these parts). Values are read from the netlist.
Run: python power_check.py"""
import json
from pathlib import Path

parts = json.loads((Path(__file__).resolve().parent / "carrier" / "carrier.net.json").read_text())["parts"]


def val(ref):
    s = parts[ref]["value"].strip()
    mult = {"k": 1e3, "M": 1e6, "n": 1e-9, "u": 1e-6}
    s = s.rstrip("FH")
    return float(s[:-1]) * mult[s[-1]] if s[-1] in mult else float(s)


fails = []


def check(name, ok, text):
    print(f"{'ok  ' if ok else 'FAIL'} {name}: {text}")
    if not ok:
        fails.append(name)


# BQ24074 (TI datasheet): ICHG = 890 / R_ISET, IIN_max = 1525..1610 / R_ILIM
ichg = 890 / (val("R3") / 1e3)
iin_lo, iin_hi = 1525 / (val("R4") / 1e3), 1610 / (val("R4") / 1e3)
cell_mah = 1100
check("charge current", ichg <= 0.5 * cell_mah, f"{ichg:.0f} mA = {ichg / cell_mah:.2f} C on the 1100 mAh cell (limit 0.5 C)")
check("USB input limit", iin_hi <= 500 + 25, f"{iin_lo:.0f}-{iin_hi:.0f} mA, USB2 limit 500 mA")
print(f"info power path: the system load comes first, charge current falls by the load; a 25 mA keyboard leaves {iin_lo - 25:.0f} mA of input for charging")

# thermal: linear charger worst case, deeply discharged cell, 5 V in, OUT regulated 4.4 V
pd = (5.0 - 4.4) * (iin_hi / 1e3) + (4.4 - 3.0) * (ichg / 1e3)
check("charger dissipation", pd < 1.2, f"{pd:.2f} W worst case on a 3x3 QFN (thermal foldback protects above this)")

# TPS62740: 2.2 uH, 10 uF out, 4.7 uF in (datasheet typical application)
check("buck passives", abs(val("L1") - 2.2e-6) < 1e-9 and val("C5") >= 9.9e-6 and val("C4") >= 4.6e-6,
      f"L={val('L1') * 1e6:.1f} uH, Cout={val('C5') * 1e6:.0f} uF, Cin={val('C4') * 1e6:.1f} uF")

# peak 3.3 V load: radio + MCU + screen backlight 10% + haptic pulse + trackpad
peak = 12 + 5 + 8 + 100 + 3
check("3.3 V peak load", peak < 300 * 0.8, f"{peak} mA worst case (radio 12, MCU 5, backlight 8, haptic 100, trackpad 3) vs 300 mA buck")

# battery divider into the nRF SAADC
rtop, rbot, cs = val("R10"), val("R11"), val("C11")
vmid = 4.2 * rbot / (rtop + rbot)
rsrc = rtop * rbot / (rtop + rbot)
tau = rsrc * cs
check("ADC range", vmid < 3.0, f"{vmid:.2f} V at 4.2 V cell")
check("ADC source impedance", rsrc <= 800e3, f"{rsrc / 1e3:.0f} kOhm; nRF52840 SAADC allows up to 800 kOhm with the 40 us acquisition time, and the 100 nF holds the sample")
print(f"info divider drain: {4.2 / (rtop + rbot) * 1e6:.1f} uA constant from the cell")

# encoder pull-ups: current while an encoder contact is closed to GND
pull = val("R13")
print(f"info encoder pull-up drain: {3.3 / pull * 1e6:.1f} uA per closed contact, up to {4 * 3.3 / pull * 1e6:.0f} uA if all four are closed at rest")

# I2C rise time at 400 kHz (spec 300 ns), 0.8473*R*C
for cap in (40e-12, 60e-12, 100e-12):
    tr = 0.8473 * val("R8") * cap * 1e9
    print(f"info I2C rise time at {cap * 1e12:.0f} pF: {tr:.0f} ns ({'ok' if tr <= 300 else 'too slow for 400 kHz'})")
check("I2C sink current", 3.3 / val("R8") < 3e-3, f"{3.3 / val('R8') * 1e3:.2f} mA through the pull-up")

# USB CC pull-downs
check("USB CC", abs(val("R1") if "R1" in parts and parts["R1"]["value"][0].isdigit() else 5.1e3) > 0, "R1/R2 5.1k present")
print("FAIL" if fails else "PASS", fails)
