# Verified parts list — Sofle RGB one-controller couch keyboard

Prepared 9 November 2026. Prices are **one-piece India website prices** observed during research. Stock and checkout totals can change. Shipping, import fees, tax, PCB assembly, and 3D printing are **not included**.

Status key: **Select** = exact orderable manufacturer part; **Check** = exact product exists, but fit or supply detail remains open; **Design** = custom item that requires layout.

## Main components

| Qty | Item | Manufacturer part number | Source / purchase link | INR each | Status |
|---:|---|---|---|---:|---|
| 1 | Single BLE/USB MCU module; 61-pad, 48 GPIO | Seeed `113990582` (Raytac `MDBT50Q-1MV2`) | [DigiKey India](https://www.digikey.in/en/products/detail/seeed-technology-co-ltd/113990582/9697025) | 1,141.32 | Select; Raytac antenna clearance required |
| 1 | 40 mm round trackpad, **SPI**, adhesive overlay | Cirque `TM040040-2024-301` | [Mouser India](https://www.mouser.in/en/ProductDetail/Cirque/TM040040-2024-301) | 920.05 | Select; 34 in stock at check, 31-week factory lead |
| 1 | Single-cell charger with USB/system power path | TI `BQ24074RGTR` | [DigiKey India](https://www.digikey.in/en/products/detail/texas-instruments/BQ24074RGTR/5142985) | 232.19 | Select; external TS/current circuit required |
| 1 | 3.3 V low-power buck, 300 mA | TI `TPS62740DSST` | [DigiKey India](https://www.digikey.in/en/products/detail/texas-instruments/TPS62740DSST/4503015) | 189.19 | Select; no high-power RGB load |
| 1 | Protected single-cell 1100 mAh LiPo with 75 mm cable | NOVA `603450` | [Robu India](https://robu.in/product/nova-603450-1100mah-3-7v-micro-lipo-battery-pack/) | 239.00 | Check pack dimensions, lead termination, max charge current |
| 1 | USB-C, USB 2.0, 24-pin form | GCT `USB4085-GF-A` | [DigiKey India](https://www.digikey.in/en/products/detail/gct/USB4085-GF-A/9859733) | 86.95 | Select; footprint/port position to check |
| 1 | Right-angle slide SPDT, 5 mm actuator | E-Switch `EG1213` | [DigiKey India](https://www.digikey.in/en/products/detail/e-switch/EG1213/101735) | 72.28 | Check against case slot |

**Main-component subtotal:** **₹2,880.98**. This excludes connectors, flex cables, protection, passive parts, PCB fabrication, assembly, printing, shipping, and taxes. It is **not** the complete project price.

## Electrical connectors, cables, and safety parts

| Qty | Item | Manufacturer part number | Purchase link | INR each | Status |
|---:|---|---|---|---:|---|
| 4 | 16-pin 0.5 mm FFC lock sockets; one per PCB adapter and two on carrier | Molex `5034801600` | [DigiKey India](https://www.digikey.in/en/products/detail/molex/5034801600/2356627) | 147.42 | Select; reversible contacts, verify actual cable pin order |
| 1 | Left 16-pin FFC, 203 mm, opposite-side contacts | GCT `05-16-D-0203-A-4-06-4-T` | [DigiKey India](https://www.digikey.in/en/products/detail/gct/05-16-D-0203-A-4-06-4-T/21266407) | 127.66 | Check length after measuring route |
| 1 | Right 16-pin FFC, 50 mm, same-side contacts | GCT `05-16-A-0050-A-4-06-4-T` | [DigiKey India](https://www.digikey.in/en/products/detail/gct/05-16-A-0050-A-4-06-4-T/21266921) | 107.47 | Check length after measuring route |
| 1 | 12-pin 0.5 mm vertical FFC host socket | Molex `0781271220` | [DigiKey India](https://www.digikey.in/en/products/detail/molex/0781271220/9693742) | 140.71 | Select; active replacement for obsolete `78127-1128` |
| 1 | Trackpad 12-pin 0.5 mm FFC, about 100 mm | GCT `05-12-D-0101-A-4-06-4-T` | [DigiKey India](https://www.digikey.in/en/products/detail/gct/05-12-D-0101-A-4-06-4-T/21266649) | 111.79 | Check contact side against Cirque connector |
| 1 | 2-pin 2.0 mm JST-PH PCB header | JST `S2B-PH-K-S` | [DigiKey India](https://www.digikey.in/en/products/detail/jst-sales-america-inc/S2B-PH-K-S/926626) | 11.47 | Select; verify polarity before insertion |
| 1 | JST-PH 2-way matching housing | JST `PHR-2` | [DigiKey India search](https://www.digikey.in/en/products/result?keywords=PHR-2) | — | Check battery cable type |
| 2 | JST-PH crimp sockets, 24–30 AWG | JST `SPH-002T-P0.5S` | [DigiKey India](https://www.digikey.in/en/products/detail/jst-sales-america-inc/SPH-002T-P0-5S/527358) | 3.91 | Check wire size; needs crimp tool |
| 1 | Cell temperature sensor, NTC 10 kΩ B≈3977 | Vishay `NTCLE100E3103JB0` | [DigiKey India](https://www.digikey.in/en/products/detail/vishay-beyschlag-draloric-bc-components/NTCLE100E3103JB0/769411) | 57.07 | Check NTC network against TI TS thresholds |
| 1 | USB D+/D− ESD diode array | ST `USBLC6-2SC6` | [DigiKey India](https://www.digikey.in/en/products/detail/stmicroelectronics/USBLC6-2SC6/1121688) | 51.60 | Check active stock; alternate `USBLC6-2SC6Y` footprint differs |

The **tracked part subtotal** is **₹4,086.25** before passive components, custom PCBs, 3D printing, tax, or shipping. The JST-PH housing has no verified unit price. The chosen FFC lengths and orientation need one physical measurement.

## Custom and supporting parts — fabrication and values pending

| Qty | Item | Specification | Current status |
|---:|---|---|---|
| 1 | New MCU carrier PCB | 54 × 20 mm concept; nRF module, charger, regulator, USB-C, switch, FFC connectors, SWD | **Design**: full schematic and RF layout not yet made |
| 1 | Left Pro Micro socket adapter PCB | 24 pad footprint to 16-way FFC; uses only 14 active nets | **Design**: mirrored footprint and PCB clearance to check |
| 1 | Right Pro Micro socket adapter PCB | 24 pad footprint to 16-way FFC; uses only 14 active nets | **Design**: encoder/USB clearance to check |
| 1 | Main unibody case | 390 × 135.85 mm upper shell, source-shaped key openings | Preliminary OpenSCAD model |
| 1 | Bottom service cover | One 1100 mAh cell bay | Preliminary OpenSCAD model |
| 1 | Cirque bracket | 40 mm round sensor retainer; four M2 fixing points | Preliminary OpenSCAD model |
| 1 set | Printed-case hardware | M2 heat-set inserts, matching short M2 screws, thin nonconductive sensor gasket, cell-safe adhesive | Select after actual wall and boss print test |
| 2 | USB-C CC resistors | 5.1 kΩ ±1% each | Required on carrier |
| 1 | TPS62740 inductor | 2.2 µH, saturation current selected to TI design | Exact vendor part after PCB layout |
| several | Input/output capacitors | Per TI charger, regulator, and Raytac reference | Values and footprints after schematic review |
| several | Charger resistors and NTC network | Set USB input limit and cell charge current conservatively | Do not order until battery charge rating verified |
| 1 | Cell voltage-sense divider | High-impedance divider and SAADC filter | Design pending |
| 1 | SWD programming probe | Nordic/J-Link or compatible CMSIS-DAP | Required if no probe is already owned; not a keyboard part |

### Source warnings

1. **Azoteq TPS43-201 is end-of-life.** It is excluded from this design.
2. **Cirque `TM040040-2024-301` is SPI.** The `2023` suffix is I2C. The manufacturer PDF establishes this distinction.
3. **Mouser's available Cirque stock is limited.** The current manufacturer's Gen6s `TM040040-1-306I` is a different part. Do not substitute it without a new connector and firmware review.
4. The battery's protection board does not replace cell temperature monitoring. Do not connect a bare unknown LiPo to an untested charger PCB.
5. The existing RGB LED rail is not a valid 3.3 V load for the selected 300 mA low-power buck. The first build leaves RGB off.

