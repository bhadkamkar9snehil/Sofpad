# Sofle RGB couch keyboard conversion

This package combines **two existing Sofle RGB PCBs** and **one Azoteq TPS43 trackpad** in a **single-piece 3D-printed lower case**. It retains both **Pro Micro ATmega32U4** controllers and the internal TRRS link. This is a **wired USB prototype** until the controllers are replaced for wireless use.

The Pro Micro's operating voltage is not known yet. The wiring document gives a **5 V-safe design** and requires a voltage check before installation.

## Included files

| File | Purpose |
|---|---|
| `SofleRGB_Couch_Case.scad` | Editable parametric case source. Open this file first. |
| `sofle_rgb_geometry.scad` | Exact outer PCB perimeter and seven M2 hole coordinates, from the official Sofle RGB KiCad file. |
| `SofleRGB_Couch_Case.stl` | Ready-generated full case, for fit review and slicing. |
| `TPS43_Fit_Coupon.stl` | Small trackpad pocket test before printing the full case. |
| `QMK_and_wiring.md` | Electrical plan, FFC pinout, safety checks, and QMK configuration fragments. |
| `extract_sofle_geometry.py` | Optional generator if you need geometry from another `.kicad_pcb` file. |
| `validate_stl.py` | Test the exported STL for size and closed, connected mesh. |
| `CAD_layout.svg` / `CAD_layout.png` | Top-down placement plan based on the official PCB perimeter. |
| `render_layout.py` | Regenerate the top-down placement plan. |
| `LICENSE-SOFLE.txt` | Original MIT license for the source PCB design. |

## Layout

The stock case parameters produce:

| Dimension | Value |
|---|---:|
| PCB envelope, each half | 143.50 × 111.85 mm |
| Whole case | 389.99 × 135.85 × 15.00 mm |
| Gap between the two PCB envelopes | 17 mm |
| Right-side trackpad area | 66 mm wide |
| TPS43 sensor/module pocket | 44.2 × 41.2 mm |
| PCB underside above case bottom | 12 mm |
| PCB mounting points | 7 per side (14 total), from source KiCad |

**This requires a printer bed larger than 390 × 136 mm**, plus slicer margins. If your printer is smaller, use a print service with a large-format printer. A split-for-print design would no longer be single-piece.

The lower case is one connected printable object. The shell has open-top PCB cavities and integrated mounting bosses. The right-side trackpad deck has short-span, open-bottom cellular pockets to reduce material. The bridge groove sits opposite the source TRRS jack location. The board outlines remain visible; this case does not cover the keys or existing PCB top plates.

## Which PCB fits?

The 2D outline and M2 hole coordinates come from:

- Design: https://github.com/josefadamcik/SofleKeyboard
- File: `Sofle_RGB/PCB/SofleKeyboard.kicad_pcb`
- Commit: `fb294f7c58d0f91c379a9ef339159d4d056643e9`

The model reflects this **specific official RGB revision**. Keyhive, prebuilt, and other Sofle RGB variants may change the PCB outline, controller location, hole positions, or electrical pinout.

Before using an STL, compare these items with your **actual** hardware:

1. PCB width and height.
2. Seven M2 mounting-hole locations on each half.
3. TRRS jack position and connector projection.
4. Micro-USB port clearance with the case, keycaps, and cable.
5. Under-PCB component height, including RGB LEDs and Pro Micro solder joints.
6. Trackpad module size, FFC direction, and overlay thickness.

If the actual board differs, regenerate `sofle_rgb_geometry.scad` from its correct KiCad PCB file. The extractor needs KiCad's Python bindings.

## Change the case

1. Open `SofleRGB_Couch_Case.scad` in OpenSCAD.
2. Keep `part = "assembly"` to inspect the PCB placement and touchpad.
3. Set `part = "case"` for the production solid.
4. Adjust `half_gap`, `pad_zone_w`, `pad_w`, `pad_h`, `pad_recess_depth`, and other named parameters.
5. Render with **F6** and export an STL.

CLI example:

```bash
openscad --export-format binstl \
  -o SofleRGB_Couch_Case.stl \
  -D 'part="case"' SofleRGB_Couch_Case.scad
python validate_stl.py SofleRGB_Couch_Case.stl
```

To export the small test piece:

```bash
openscad --export-format binstl \
  -o TPS43_Fit_Coupon.stl \
  -D 'part="pad_coupon"' SofleRGB_Couch_Case.scad
```

## Print and assemble

1. Print `TPS43_Fit_Coupon.stl` first. Test the physical pad and its overlay.
2. Measure the full PCB and confirm the 14 case-hole coordinates. Do not force a PCB onto unmatched bosses.
3. Confirm the printer can fit the complete case in its required orientation.
4. Print the full case flat on its underside. Use material and nozzle settings that support **10–12 mm bridges** in the cellular pockets. Inspect the slicer preview for unsupported regions.
5. Insert the M2 heat-set inserts into the 14 mounting bosses. **Verify insert diameter against the actual insert**; `insert_hole_d=3.2` is an initial value, not a vendor specification.
6. Place both PCB halves in the open cavities. Keep their existing top plates and key switches.
7. Fit the short TRRS cable in the center channel. Connect or disconnect it only with power off.
8. Fit the trackpad and its FFC. Mount the regulator and level shifter in the right PCB cavity without contact with solder joints.
9. Secure wires with insulated tape or clips. Keep them away from switch pins and RGB LED pads.
10. Check I²C voltage and function before applying the final trackpad overlay.

## Status and limits

- **CAD render test:** OpenSCAD generated the full STL and the fit coupon successfully.
- **Mesh test:** Both files are one connected, closed shell, with no open edges.
- **Physical fit:** Not yet tested against your physical PCB, printed case, or selected TPS43 part.
- **Electrical:** The 5 V-safe wiring plan accounts for Azoteq's voltage limit. Confirm the Pro Micro voltage before wiring. The circuit is not built or tested.
- **Firmware:** QMK settings are a starting point. No flashable firmware is supplied without identifying the exact RGB PCB and current keymap.
- **Wireless:** Not part of this ATmega32U4 prototype.

## Source references

- Official PCB design (MIT): https://github.com/josefadamcik/SofleKeyboard
- QMK pointing-device documentation: https://docs.qmk.fm/features/pointing_device
- Azoteq TPS43/TPS65 datasheet: https://www.azoteq.com/images/stories/pdf/proxsense_i2c_trackpad_datasheet.pdf
