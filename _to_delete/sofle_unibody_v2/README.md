# Sofle RGB couch keyboard — integrated trackpad enclosure

This is a parametric **CAD prototype**. The top shell is one continuous part.
It holds both original Sofle RGB boards and one Azoteq TPS43-format touchpad.
The bottom panel is removable for battery service.

## Included parts

| File | Purpose |
|---|---|
| `SofleRGB_Unibody_Couch.scad` | Parametric source for all three parts |
| `sofle_rgb_geometry.scad` | PCB dimensions and 7 M2 holes per half, extracted from source KiCad file |
| `sofle_components.scad` | Source switch and encoder locations |
| `Unibody_Shell.stl` | Continuous upper enclosure with switch holes and rear cutouts |
| `Service_Bottom.stl` | Removable bottom with screw holes and four battery guides |
| `TPS43_Retainer.stl` | Four-screw touchpad retainer with cable exit |
| `layout_components.json` | Actual source key coordinates for rendering |
| `render_hero.png` | Assembled concept render based on CAD |
| `render_top.png` | Top-down assembled concept render |
| `render_rear_ports.png` | Rear edge and external connector cutouts |
| `render_service.png` | Concept service view; not an assembly specification |

## Current envelope

* Main upper shell: **390.0 × 135.85 × 17.5 mm**. Keycaps and encoders extend above 17.5 mm.
* Bottom cover: **382.49 × 128.35 × 1.8 mm**, plus 2.2 mm high local battery guides.
* One cell envelope reserved: **42 × 31 × 6 mm**. It is an envelope, not a selected battery product.
* Trackpad: 43 × 40 mm nominal sensor, with a **47.5 × 44 mm** protective overlay and a **59 × 54 mm** retaining frame.
* Rear connector hole: **11 × 5.1 mm**, for a USB-C panel connector. Rear power switch hole: **10 × 4.2 mm**.
* Two internal USB-C flange bosses have a parametric **21 mm M2 pitch**. Confirm the actual extension part before print.
* Front/top has 58 switch cutouts and two encoder shaft cutouts, based on the official Sofle RGB board.

## Configuration

Open `SofleRGB_Unibody_Couch.scad` in OpenSCAD.
Set `part` to `"shell"`, `"bottom"`, or `"trackpad_frame"`.
Edit the named parameters at the top. Export each part as STL.

The shape uses the Sofle RGB KiCad source at commit
`fb294f7c58d0f91c379a9ef339159d4d056643e9` from
https://github.com/josefadamcik/SofleKeyboard.

## Trackpad installation

1. Bond the sensor to the approved protective overlay. Follow the sensor vendor's bonding method.
2. Lay the overlay into the recessed opening from above. The recessed lip supports the overlay.
3. Apply thin, compressible foam around the sensor perimeter. Keep foam away from the active area and the FFC cable.
4. Pass the FFC tail through the frame cable notch.
5. Install the open-centre retainer from below. Use four M2 fasteners into the internal inserts.
6. Select shims after measuring the actual module, overlay, and foam thickness. The retainer must secure the module without bending it.

The top trackpad surface is replaceable. It is not printed plastic.
The retainer prints separately. Do not put a screw, battery, or rigid protrusion behind the active sensor area.

## Single-battery electrical concept

The wireless plan retains the two PCB halves but replaces the two Pro Micros with two nRF52840 Pro Micro-compatible controllers.
The **right controller is the ZMK central** because it connects to the trackpad.
The controllers exchange key events by Bluetooth Low Energy (BLE), inside one shared case.

```text
ONE protected 3.7 V LiPo, 1000 mAh target
  positive -> correctly sized fuse -> master slide switch -> battery-positive branches
                                              |-> right nRF52840 B+
                                              |-> left nRF52840 B+
  negative -------------------------------------> both B- / battery ground

Rear panel USB-C socket -> short USB-C extension -> RIGHT controller USB-C
RIGHT controller I2C + power + reset/ready GPIO -> trackpad module
```

**Important: This is not a released wiring schematic.** The nice!nano maker does not support powering one split controller from the other or through TRRS. A direct, fused two-branch battery feed is a separate proposed circuit. Check controller charger and power-path schematics before connecting it. Do not connect VCC rails through TRRS. Do not connect both controllers to USB at the same time. Cover the second controller's USB port within the service enclosure.

The nice!nano has a built-in LiPo charger. Set its solder jumper only after checking the chosen protected cell's charge rating. A 1000 mAh pack generally matches its listed 500 mA mode. With the proposed upstream power switch, charging requires the switch to be **ON**. The charger does not charge a disconnected cell.

Turn off the Sofle RGB LEDs in battery mode. LED power can dominate battery use. Check the actual pin use, touchpad voltage, and ZMK driver configuration before ordering wireless controllers.

## Manufacturing checks before printing the full body

- Measure actual populated PCB stack height and connector locations. A Pro Micro-to-nice!nano swap can change controller height and USB clearance.
- Print a 30 × 40 mm switch-cutout test first. Confirm MX switch retention in a 1.8 mm printed panel.
- Confirm OLED presence. The default `oled_windows=false` closes the OLED positions; installed OLEDs will require clearance.
- Check PCB orientation and all mount hole offsets against your assembled boards.
- Measure the exact trackpad SKU, FFC exit direction, overlay thickness, and bracket standoffs.
- Select the actual battery model. Test swelling clearance, temperature, protection electronics, and connector accessibility.
- Measure the selected USB-C panel extension and slide switch. The USB-C mount is adjustable; the slide switch still needs a part-specific retaining clip.
- Divide the case or use a printer with at least 400 mm of bed space. This version is a **single-piece upper shell** and will not fit common 220 mm beds.

The three STL meshes passed closed-surface and connected-solid validation.
They have **not** passed a physical fit test. Rendered keycaps are illustrative.

## Sources

* SofleKeyboard: https://github.com/josefadamcik/SofleKeyboard
* nice!nano battery and charging: https://nicekeyboards.com/docs/nice-nano/
* nice!nano split safety FAQ: https://nicekeyboards.com/docs/nice-nano/faq/
* ZMK split keyboard architecture: https://zmk.dev/docs/features/split-keyboards
* Example Azoteq IQS5xx ZMK driver: https://github.com/AYM1607/zmk-driver-azoteq-iqs5xx

The TPS43 is listed as end-of-life by the example ZMK driver author. Confirm availability and pinout. The driver lists later models but has not confirmed testing on them.

