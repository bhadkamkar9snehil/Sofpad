# Sofle RGB couch keyboard — single nRF52840, single battery, Azoteq TPS43 I2C

Engineering package R3 · 9 November 2026

## What is designed

- Both original Sofle RGB PCB halves remain in one printed upper shell.
- Both existing ATmega32U4 Pro Micro boards are removed. Each socket receives a **passive adapter**.
- Two internal 16-way flex cables connect the adapters to **one** nRF52840 carrier PCB.
- Both halves share five row inputs. Each half keeps six separate column outputs and two encoder signals.
- One **Azoteq TPS43-201A-S** 43 × 40 mm I2C trackpad sits in the right zone. **CAD still models the old round Cirque. Update it next.**
- One protected 1100 mAh LiPo supplies the complete unit through a 3.3 V regulator.
- The charger and USB HID data share one rear USB-C port. A rear switch controls regulator enable.
- One MCU firmware image will provide Windows USB and BLE keyboard/mouse HID.

The source KiCad PCB was checked. The wiring architecture is feasible with one nRF52840 module. **Custom PCBs, charge-current values, antenna layout, and mechanical fit of purchased components require further engineering. This package is not fabrication-ready.**

## Package contents

| File | Purpose |
|---|---|
| `ELECTRICAL_REVIEW.md` | Datasheet check of the electronics, trackpad choice, open risks |
| `ARCHITECTURE.md` | Existing PCB nets, FFC wire table, MCU pin map, TPS43 I2C pins, charging path, engineering gates |
| `BOM.md` | Source-linked parts list with exact manufacturer numbers and India prices |
| `BOM.csv` | Machine-readable component quantities, prices, and status |
| `verify_matrix.py` | Source KiCad net/pad checker (uses KiCad `pcbnew`) |
| `source_pinmap.json` | Output of KiCad net verification |
| `reference/Sofle_RGB/PCB/SofleKeyboard.kicad_pcb` | Exact upstream source PCB used for the verification |
| `cad/SofleRGB_SingleController_Cirque.scad` | Editable parametric case geometry |
| `cad/sofle_rgb_geometry.scad` | Source-derived Sofle switch and mounting positions |
| `cad/sofle_components.scad` | Source-derived board footprint and component reference points |
| `cad/Unibody_Shell.stl` | Preliminary continuous upper shell for 3D printing |
| `cad/Service_Bottom.stl` | Preliminary removable bottom cover |
| `cad/Cirque40_Retainer.stl` | **Obsolete** round Cirque retaining plate. Redo for the TPS43. |
| `cad/layout_components.json` | Key/encoder positions for illustration |
| `cad/render_blender.py` | Code-native Blender rendering of CAD and illustrative keycaps |
| `cad/render_*.png` | Concept images rendered from the actual STL geometry |
| `cad/verify_stl.py` | Checks that all three exported STL triangle meshes are closed |
| `LICENSE-SOFLE.txt` | Upstream license for included PCB and derived case geometry |

## Build state

**Verified:** source PCB matrix, pad nets, two encoder signal pairs, module pin budget, selected trackpad communication type, exact listed core part numbers, and exported preliminary shell geometry. The three STL files passed a closed-mesh edge check.

**Not verified:** actual left/right PCB socket orientation, folded FFC routing/contact orientation, USB-C connector alignment, printed tolerances, trackpad retention/notches, selected cell's protected dimensions and charge current, RF performance, firmware, and charger safety.

RGB LEDs and OLED displays remain off in this low-power first revision. The source PCB has not been cut or rewired. The battery charger, USB, and nRF require **new carrier PCB circuitry**; the old Pro Micro boards cannot provide wireless service.

## Print and fit procedure

1. Open `cad/SofleRGB_SingleController_Cirque.scad` in OpenSCAD.
2. Adjust dimensions after measuring the purchased trackpad and cell.
3. Export each `part`: `shell`, `bottom`, and `trackpad_frame`.
4. Print a local trackpad, USB-C, and switch fit sample first.
5. Test switch alignment, PCB mounting, and access before printing the complete shell.

The main upper shell is about **390 × 136 mm**. It needs a large-format print bed or a printing service with sufficient build area and margin.

Source project: https://github.com/josefadamcik/SofleKeyboard

PCB commit used: `fb294f7c58d0f91c379a9ef339159d4d056643e9`.

The case is based on the open Sofle PCB geometry. Preserve upstream license attribution when you share adapted files.
