"""Sofpad R3 carrier PCB netlist. Run:  python carrier.py  (writes carrier/carrier.kicad_sch + net.json)

Sources for every value: datasheets in docs/hardware (BQ24074 eqs 1-7, TPS62740 table 1),
Raytac MDBT50Q-1MV2 pad sheet, Azoteq TPS65 datasheet v1.02 table 3.1.
"""
import sys
from pathlib import Path

import kigen
import kilib

HERE = Path(__file__).resolve().parent

# ---- custom symbol: TPS62740DSS (12-pin WSON + thermal pad). Pinout from TI SLVSB02B. ----
_pins_l = [("1", "VIN", "power_in"), ("2", "SW", "output"), ("3", "GND", "power_in"), ("4", "CTRL", "input"),
           ("5", "VOUT", "input"), ("6", "LOAD", "output")]
_pins_r = [("12", "EN", "input"), ("11", "VSEL1", "input"), ("10", "VSEL2", "input"), ("9", "VSEL3", "input"),
           ("8", "VSEL4", "input"), ("7", "PG", "open_collector")]
_sym = ['(symbol "Sofpad:TPS62740" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
        '  (property "Reference" "U" (at 0 10.16 0) (effects (font (size 1.27 1.27))))',
        '  (property "Value" "TPS62740DSS" (at 0 -10.16 0) (effects (font (size 1.27 1.27))))',
        '  (property "Footprint" "Package_SON:WSON-12-1EP_3x2mm_P0.5mm_EP1x2.65" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        '  (property "Datasheet" "https://www.ti.com/lit/ds/symlink/tps62740.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        '  (symbol "TPS62740_0_1" (rectangle (start -10.16 8.89) (end 10.16 -8.89) (stroke (width 0.254) (type default)) (fill (type background))))',
        '  (symbol "TPS62740_1_1"']
_custom_pins = []
for i, (n, name, t) in enumerate(_pins_l):
    y = 6.35 - i * 2.54
    _sym.append(f'    (pin {t} line (at -12.7 {y:.2f} 0) (length 2.54) (name "{name}" (effects (font (size 1.27 1.27)))) (number "{n}" (effects (font (size 1.27 1.27)))))')
    _custom_pins.append((n, name, t, -12.7, y, 0))
for i, (n, name, t) in enumerate(_pins_r):
    y = 6.35 - i * 2.54
    _sym.append(f'    (pin {t} line (at 12.7 {y:.2f} 180) (length 2.54) (name "{name}" (effects (font (size 1.27 1.27)))) (number "{n}" (effects (font (size 1.27 1.27)))))')
    _custom_pins.append((n, name, t, 12.7, y, 180))
_sym.append('    (pin passive line (at 0 -11.43 90) (length 2.54) (name "EP" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))')
_custom_pins.append(("13", "EP", "passive", 0.0, -11.43, 90))
_sym.append("  )")
_sym.append(")")
kigen.CUSTOM_SYMBOLS["Sofpad:TPS62740"] = ("\n".join(_sym), _custom_pins)

d = kigen.Design("carrier")
R0402 = "Resistor_SMD:R_0402_1005Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"

d.part("U1", "RF_Module", "MDBT50Q-1MV2", "RF_Module:Raytac_MDBT50Q", "MDBT50Q-1MV2")
d.part("U2", "Battery_Management", "BQ24074RGT", "Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm", "BQ24074RGTR")
d.part("U3", "Sofpad", "TPS62740", "Package_SON:WSON-12-1EP_3x2mm_P0.5mm_EP1x2.65", "TPS62740DSST")
d.part("U4", "Driver", "DRV2605LDGS", "Package_SO:MSOP-10_3x3mm_P0.5mm", "DRV2605LDGSR")
d.part("U5", "Sensor_Motion", "LIS3DH", "Package_LGA:LGA-16_3x3mm_P0.5mm_LayoutBorder3x5y", "LIS3DHTR")
d.part("U6", "Power_Protection", "USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", "USBLC6-2SC6")
d.part("J1", "Connector", "USB_C_Receptacle_USB2.0_16P", "Connector_USB:USB_C_Receptacle_GCT_USB4085", "GCT USB4085-GF-A")
d.part("SW1", "Switch", "SW_SPDT", "Button_Switch_SMD:SW_SPDT_PCM12", "C&K PCM12SMTR")
d.part("J2", "Connector_Generic", "Conn_01x02", "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", "Battery S2B-PH-K-S")
d.part("J3", "Connector_Generic", "Conn_01x02", "Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical", "Cell NTC")
d.part("J4", "Connector_Generic", "Conn_01x02", "Connector_JST:JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal", "LRA SM02B-SRSS-TB")
d.part("J5", "Connector_Generic", "Conn_01x08", "Connector_JST:JST_PH_S8B-PH-K_1x08_P2.00mm_Horizontal", "Screen S8B-PH-K-S")
d.part("J6", "Connector_Generic", "Conn_01x06", "Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal", "TPS65 breakout SM06B-SRSS-TB")
d.part("J7", "Connector_Generic", "Conn_01x16", "Connector_FFC-FPC:Hirose_FH12-16S-0.5SH_1x16-1MP_P0.50mm_Horizontal", "Left FFC FH12-16S-0.5SH")
d.part("J8", "Connector_Generic", "Conn_01x16", "Connector_FFC-FPC:Hirose_FH12-16S-0.5SH_1x16-1MP_P0.50mm_Horizontal", "Right FFC FH12-16S-0.5SH")
for i, v in enumerate(["SWDIO", "SWDCLK", "RESET", "3V3", "GND"], 1):
    d.part(f"TP{i}", "Connector", "TestPoint", "TestPoint:TestPoint_Pad_D1.0mm", v)

# passives: (ref, value, footprint)
for ref, val in [("R1", "5.1k"), ("R2", "5.1k"), ("R3", "2.0k"), ("R4", "3.3k"), ("R5", "47k"), ("R6", "3.0k"),
                 ("R7", "100k"), ("R8", "4.7k"), ("R9", "4.7k"), ("R10", "1M"), ("R11", "1M"), ("R12", "10k")]:
    d.part(ref, "Device", "R", R0402, val)
for ref, val, fp in [("C1", "1uF", C0402), ("C2", "10uF", C0603), ("C3", "10uF", C0603), ("C4", "4.7uF", C0603),
                     ("C5", "10uF", C0603), ("C6", "10uF", C0603), ("C7", "100nF", C0402), ("C8", "1uF", C0402),
                     ("C9", "1uF", C0402), ("C10", "100nF", C0402), ("C11", "100nF", C0402), ("C12", "10uF", C0603)]:
    d.part(ref, "Device", "C", fp, val)
d.part("L1", "Device", "L", "Inductor_SMD:L_0805_2012Metric", "2.2uH")

c = d.conn
# ---------------- USB-C, ESD, VBUS ----------------
c("GND", "J1.A1", "J1.B1", "J1.A12", "J1.B12", "J1.SH", "U6.2")
c("VBUS", "J1.A4", "J1.B4", "J1.A9", "J1.B9", "U6.5", "U2.13", "C1.1", "U1.32")
c("CC1", "J1.A5", "R1.1")
c("CC2", "J1.B5", "R2.1")
c("GND", "R1.2", "R2.2", "C1.2")
c("USB_DP", "J1.A6", "J1.B6", "U6.1", "U6.6", "U1.35")
c("USB_DM", "J1.A7", "J1.B7", "U6.3", "U6.4", "U1.34")
# ---------------- BQ24074 charger and power path ----------------
c("VSYS", "U2.10", "U2.11", "C2.1", "U3.1", "C4.1", "R7.1", "U3.11", "U3.10", "U3.9", "U3.8", "SW1.1")
c("VBAT", "U2.2", "U2.3", "C3.1", "J2.1", "R10.1")
c("GND", "U2.8", "U2.17", "U2.4", "U2.5", "C2.2", "C3.2", "J2.2", "C4.2")
c("EN1", "U2.6", "R7.2")
c("TS", "U2.1", "J3.1")
c("GND", "J3.2")
c("ISET", "U2.16", "R3.1")
c("ILIM", "U2.12", "R4.1")
c("ITERM", "U2.15", "R6.1")
c("TMR", "U2.14", "R5.1")
c("GND", "R3.2", "R4.2", "R5.2", "R6.2")
c("CHG", "U2.9", "U1.4")
c("PGOOD", "U2.7", "U1.5")
# ---------------- TPS62740 3.3 V buck and slide switch ----------------
c("SW_NODE", "U3.2", "L1.1")
c("+3V3", "L1.2", "U3.5", "C5.1", "C6.1")
c("GND", "U3.3", "U3.4", "U3.13", "C5.2", "C6.2", "SW1.3")
c("EN_SW", "U3.12", "SW1.2")
# ---------------- nRF52840 module ----------------
c("+3V3", "U1.28", "U1.30", "C7.1", "C12.1", "R8.1", "R9.1", "J5.1", "J6.4", "U4.10", "U5.1", "U5.14", "U5.8", "C8.1", "C10.1", "TP4.1")
c("GND", "C7.2", "C12.2", "C8.2", "C10.2", "TP5.1")
for gp in ("1", "2", "15", "33"):
    c("GND", f"U1.{gp}")
# find remaining GND-named module pins automatically
for p in kilib.symbol_pins("RF_Module", "MDBT50Q-1MV2"):
    if p[1] == "GND" and p[0] not in ("1", "2", "15", "33"):
        c("GND", f"U1.{p[0]}")
rows = ["37", "36", "39", "38", "41"]
for i, pad in enumerate(rows):
    c(f"ROW{i}", f"U1.{pad}", f"J7.{i + 1}", f"J8.{i + 1}")
for i, pad in enumerate(["49", "19", "16", "47", "61", "50"]):
    c(f"LEFT_COL{i}", f"U1.{pad}", f"J7.{6 + i}")
for i, pad in enumerate(["42", "44", "43", "46", "45", "48"]):
    c(f"RIGHT_COL{i}", f"U1.{pad}", f"J8.{6 + i}")
c("LEFT_ENC_A", "U1.60", "J7.12")
c("LEFT_ENC_B", "U1.56", "J7.13")
c("RIGHT_ENC_A", "U1.59", "J8.12")
c("RIGHT_ENC_B", "U1.57", "J8.13")
c("GND", "J7.14", "J8.14")
# ---------------- shared I2C bus: TPS65, DRV2605L, LIS3DH ----------------
c("SDA", "U1.20", "R8.2", "J6.6", "U4.3", "U5.6")
c("SCL", "U1.21", "R9.2", "J6.5", "U4.2", "U5.4")
c("TP_RDY", "U1.22", "J6.1")
c("TP_NRST", "U1.23", "J6.2")
c("GND", "J6.3")
c("ACC_INT", "U1.24", "U5.11")
c("GND", "U5.5", "U5.10", "U5.12", "R12.2")
c("SA0", "U5.7", "R12.1")
# ---------------- haptics ----------------
c("HAPTIC_EN", "U1.7", "U4.5")
c("DRV_REG", "U4.1", "C9.1")
c("GND", "C9.2", "U4.8", "U4.4")
c("LRA_P", "U4.7", "J4.1")
c("LRA_N", "U4.9", "J4.2")
# ---------------- screen ----------------
c("GND", "J5.2")
c("LCD_MOSI", "U1.14", "J5.3")
c("LCD_SCK", "U1.12", "J5.4")
c("LCD_CS", "U1.10", "J5.5")
c("LCD_DC", "U1.13", "J5.6")
c("LCD_RST", "U1.26", "J5.7")
c("LCD_BL", "U1.3", "J5.8")
# ---------------- battery sense, programming ----------------
c("VBAT_SENSE", "U1.11", "R10.2", "R11.1", "C11.1")
c("GND", "R11.2", "C11.2")
c("SWDIO", "U1.51", "TP1.1")
c("SWDCLK", "U1.53", "TP2.1")
c("RESET", "U1.40", "TP3.1")

d.flags = ["VBUS", "+3V3", "GND"]

if __name__ == "__main__":
    path = d.write(HERE / "carrier")
    print("wrote", path)
    print(len(d.parts), "parts,", len(d.nets), "nets")
