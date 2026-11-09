# R3 electrical review and trackpad change

Date: 9 November 2026. Status: paper review against datasheets. Nothing was built or measured.

## Result

The architecture is sound. The module pad map matches the Raytac MDBT50Q-1MV2 datasheet. The charger and buck choices work together. Several items must change before a schematic. The trackpad changes from Cirque to Azoteq.

## What was checked and passed

| Item | Check | Result |
|---|---|---|
| Module pad numbers | All pads in the GPIO table compared with Raytac spec Ver. K, section 2.5 | Match. No duplicate GPIO. |
| Restricted pads | P0.02, P1.01–P1.06 are low-frequency only (up to 10 kHz) | Used only for slow signals. Pass. |
| I2C pads | P0.04–P0.07 are unrestricted | Pass. |
| BQ24074 OUT | Regulates to 4.4 V typical | Inside TPS62740 input range (2.2–5.5 V). Pass. |
| TPS62740 3.3 V | VSEL4..1 = 1111 gives 3.3 V. It supplies 300 mA. | Pass. |
| Power budget | TPS43 about 2.2 mA, nRF BLE tens of mA at peak | Far below 300 mA. Pass. |
| NTC window | Vishay `NTCLE100E3103JB0` (B≈3977) on BQ24074 TS (75 µA, 300 mV hot, 2.1 V cold) | Trips at about 3.6 °C and 47 °C. Acceptable for LiPo. Own calculation. |

## Errors and gaps to fix in the schematic

1. **Charger resistors.** ILIM and ISET must both have resistors. The datasheet says an open ILIM or ISET disables charging.
   - Candidate: `R_ISET` = 2.0 kΩ 1% gives about 445 mA (range 398–488 mA).
   - Candidate: `R_ILIM` = 3.3 kΩ gives about 488 mA input limit (range 455–521 mA).
   - Tie EN1 high and EN2 low for the USB500 limit.
   - Confirm the NOVA 603450 maximum charge current first. Do not order resistors before that.
2. **TPS62740 pins.** EN must never float. Use the SPDT slide switch to tie EN to the BQ24074 OUT rail or to GND. CTRL must be terminated. Tie CTRL to GND if the LOAD switch is not used.
3. **Switch OFF with USB connected.** VBUS reaches the nRF VBUS pad while the nRF has no VDD. Check the Nordic nRF52840 product specification for this state. If it is not allowed, add a load switch on VBUS or enable the buck when VBUS is present.
4. **USB HID needs the switch ON.** With the switch OFF, the keyboard only charges. State this in the user manual.
5. **Matrix scan direction.** The diode cathode connects to the row. Current flows from column to row. Drive the selected column high. Set the five row inputs as pull-down. Leave unselected columns high impedance. Verify on a real board before you freeze the firmware.
6. **Encoders.** Use internal pull-ups on the A and B inputs. The common pin is GND on the source PCB. Keep encoder signals below 10 kHz on the restricted P1.03–P1.06 pads.
7. **VDDH.** Tie VDDH to VDD (normal voltage mode). The doc did not say this.
8. **Cell temperature.** The NOVA pack may have no NTC. Tape the external NTC to the cell.
9. **Battery sense divider.** Use a high-impedance divider or gate it with a FET. A fixed low-impedance divider drains the cell.

## Trackpad decision

The Cirque TM040040 was the wrong choice for this use. The reasons:

- It tracks one finger. The couch use needs two-finger scroll and right-click.
- It costs about ₹897 against about ₹423 for the TPS43.
- Its supplier lead time was 31 weeks in the earlier check.

The Azoteq TPS43-201A-S gives:

- Up to five fingers, with scroll, tap, and press-and-hold gestures in the chip.
- A 43 × 40 mm pad that fits the existing 66 mm zone and the 390 mm shell.
- I2C with four signals plus power. That frees the SPI pins.
- A ZMK driver that reports tap, two-finger tap, press-and-hold, and scroll.

### Risks of the TPS43

| Risk | Detail | Action |
|---|---|---|
| Lifecycle | The ZMK driver README says TPS43 and TPS65 are end-of-life. Mouser lists them with restock dates. Azoteq's August 2025 datasheet gives no status. | Ask Azoteq. Buy 2–3 spares now. |
| Driver maturity | The ZMK driver is third-party. It is tested only on TPS43 and TPS65. | Budget time to port to the custom carrier board. |
| ZMK pointing | ZMK pointing support is in the development docs, not in release v0.3. BLE hosts may need re-pairing. | Pin a ZMK revision. |
| Connector | The datasheet text does not give the FPC pitch. | Measure the module tail before you choose the socket. |
| Listing mismatch | Mouser says 43 × 43 mm. Azoteq says 43 × 40 mm. | Measure the delivered part. |
| Stock | Stock numbers come from search snapshots on different dates. | Check live stock. |

### Alternatives considered

| Part | Size | Why not first choice |
|---|---|---|
| Azoteq TPS65-201A-S | 65 × 49 mm, IQS550 | Larger and nicer, but the 66 mm zone is too narrow. The shell would grow by about 16 mm. Same lifecycle doubt. |
| Azoteq TPS48-P203-S | 48 × 38 mm | Driver compatibility is untested. Datasheet is from 2017. |
| Azoteq IQS9151 | Evaluation kit only (about ₹3,025) | No stock trackpad module found. |
| Cirque TM040040-2024-302 | 40 mm round, SPI | Fallback. Single finger only. Flat overlay, in stock at one snapshot. |

## Next steps

1. Choose R_ISET and R_ILIM after you read the cell datasheet.
2. Measure a TPS43 sample: outline, FPC pitch, thickness with overlay.
3. Update the CAD for a rectangular pocket.
4. Draw the carrier schematic in KiCad and run ERC.
