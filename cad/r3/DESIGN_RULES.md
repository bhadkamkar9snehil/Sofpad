# Sofpad R3 design rules

## Ergonomic decisions

| Decision | Value | Why |
|---|---|---|
| Alice-style tilt | 12° per half, backs lean toward centre | Forearms converge from the elbows to the hands. Straight halves force the wrists to bend outward. 12° is inside the usual 10–15° range. Change `ang` in the SCAD to flip or adjust it. |
| Trackpad position | Centre, front, between the thumb clusters | Either thumb reaches it without lifting the hands off the home row. A right-side pad is a one-handed device and leaves the centre empty. |
| Trackpad size | 65 × 49 mm (TPS65) | Large enough for couch use and a full thumb sweep. Landscape, aligned with the case, not tilted. |
| Encoders | Next to the thumb clusters | The thumb reaches them. The pad is wide enough to keep a gap from them (check palm rejection in firmware). |
| OLEDs | Inner edge, top, near the encoders | Visible with the hands on the keys, outside the palm area. |
| Case height | 17.5 mm under the keycaps, 2 mm top-edge radius | Low edge on the lap. The rounded edge is softer on the wrists. |
| No wrist rest | — | Use on a lap or cushion. A rest can be added as a separate part later. |
| Feet | Stick-on rubber feet | Stops sliding on a couch arm. |

## Why the mistakes happened, and the rule that stops each one

| Mistake | Root cause | Rule now enforced |
|---|---|---|
| Screw posts floating outside the case | Positions assumed a rectangular PCB. The real outline has bevelled corners. | Every plate boss must connect to the shell. `check_design.py` fails if the shell or plate is more than one connected solid. |
| Insert holes sealed inside solid | A bore opened toward a face that another part then covered. | Every hole must open to air. The same connectivity check finds the sealed void as a separate piece. |
| Non-manifold mesh (734 bad edges) | Chamfer built from stacked layers with coplanar joins. | Nested columns, never stacked coplanar layers. `verify_stl.py` must report 0 bad edges. |
| Case size surprise (390 to 449 mm) | Size was found late. | The size is printed on every build. Check it against the target before anything else. |
| Showing a render before checking it | A render hides overlaps. | Run `python check_design.py` first. It proves part overlap, cavity fit, connectivity and closed meshes. |
| Stale Cirque and TPS43 text | Renames were not searched for. | After changing a part, search all docs and scripts for the old name before committing. |
| Guessed direction of the Alice tilt | Assumption not recorded. | Assumptions go into the table above with the reason, and into a named parameter. |

## Workflow

1. Edit `Sofpad_R3_Alice.scad`.
2. `python check_design.py` must print `PASS: design checks`.
3. Export the render parts and run `render_case.py` (writes to `docs/images`).
4. Look at the render. Search for old part names. Commit.
