"""Sofpad R3 passive Pro Micro adapter netlist (one design, built twice: left and right half).

Plugs into the Sofle RGB U1 Pro Micro socket and brings 14 signals out on a 16-way FFC.
FFC pin <-> Pro Micro pad map is the table in ARCHITECTURE.md ("U1 adapter").
Run:  python adapter.py
"""
from pathlib import Path

import kigen

HERE = Path(__file__).resolve().parent
d = kigen.Design("adapter")
d.part("J1", "Connector_Generic", "Conn_01x16", "Connector_FFC-FPC:Hirose_FH12-16S-0.5SH_1x16-1MP_P0.50mm_Horizontal", "FH12-16S-0.5SH")
# Pro Micro rows: pads 1-12 down the left row, pads 24..13 down the right row (pad 24 opposite pad 1).
d.part("HL", "Connector_Generic", "Conn_01x12", "Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical", "Pro Micro left row (pads 1-12)")
d.part("HR", "Connector_Generic", "Conn_01x12", "Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical", "Pro Micro right row (pads 24-13)")


def pad(n):
    """Header pin that carries Pro Micro pad n."""
    return f"HL.{n}" if n <= 12 else f"HR.{25 - n}"


c = d.conn
for i, p in enumerate([8, 9, 10, 11, 12]):
    c(f"ROW{i}", f"J1.{i + 1}", pad(p))
for i, p in enumerate([18, 17, 16, 15, 14, 13]):
    c(f"COL{i}", f"J1.{6 + i}", pad(p))
c("ENC_A", "J1.12", pad(20))
c("ENC_B", "J1.13", pad(19))
c("GND", "J1.14", pad(23), pad(3), pad(4))

if __name__ == "__main__":
    print("wrote", d.write(HERE / "adapter"))
