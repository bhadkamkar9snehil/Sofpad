"""Build a KiCad board from <name>/<name>.net.json, route it with Freerouting, fill zones.

Run with KiCad's python:
  "%LOCALAPPDATA%\\Programs\\KiCad\\10.0\\bin\\python.exe" build_pcb.py carrier
Steps: place -> export DSN -> Freerouting (Java) -> import SES -> fill GND zones -> save.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
K = Path(r"C:\Users\Admin\AppData\Local\Programs\KiCad\10.0")
FPDIR = K / "share" / "kicad" / "footprints"
JAVA = next(Path(r"C:\Program Files\Microsoft").glob("jdk-25*/bin/java.exe"))
FREEROUTING = Path(r"C:\Users\Admin\tools\freerouting\freerouting-2.5.0.jar")
mm = pcbnew.FromMM


def vec(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def load_fp(fpid):
    lib, name = fpid.split(":")
    return pcbnew.FootprintLoad(str(FPDIR / f"{lib}.pretty"), name)


def segment(board, a, b, layer=pcbnew.Edge_Cuts, width=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(vec(*a))
    s.SetEnd(vec(*b))
    s.SetLayer(layer)
    s.SetWidth(mm(width))
    board.Add(s)


def outline(board, w, h, r=1.5):
    """Rounded rectangle on Edge.Cuts."""
    import math
    segment(board, (r, 0), (w - r, 0))
    segment(board, (w, r), (w, h - r))
    segment(board, (w - r, h), (r, h))
    segment(board, (0, h - r), (0, r))
    for cx, cy, a0 in [(w - r, r, -90), (w - r, h - r, 0), (r, h - r, 90), (r, r, 180)]:
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        start = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
        arc.SetCenter(vec(cx, cy))
        arc.SetStart(vec(*start))
        arc.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
        arc.SetLayer(pcbnew.Edge_Cuts)
        arc.SetWidth(mm(0.1))
        board.Add(arc)


def add_zone(board, layer, net, w, h, inset=0.3):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetLocalClearance(mm(0.2))
    z.SetMinThickness(mm(0.15))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in [(inset, inset), (w - inset, inset), (w - inset, h - inset), (inset, h - inset)]:
        ol.Append(mm(x), mm(y))
    board.Add(z)
    return z


def add_keepout(board, x0, y0, x1, y1):
    """Rule area: no copper, tracks or vias (antenna keep-out)."""
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask())
    ol = z.Outline()
    ol.NewOutline()
    for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
        ol.Append(mm(x), mm(y))
    board.Add(z)


def build(name, variant, w, h, layers, placement, holes, keepouts=(), mirror_x=False):
    d = HERE / name
    net = json.loads((d / f"{name}.net.json").read_text())
    pin_net = {}
    for n, pins in net["nets"].items():
        for rp in pins:
            ref, pin = rp.split(".", 1)
            pin_net[(ref, pin)] = n
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(layers)
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.15)
    ds.m_MinClearance = mm(0.15)
    ds.m_ViasMinSize = mm(0.6)
    ds.m_ViasMinAnnularWidth = mm(0.13)
    ds.m_MinThroughDrill = mm(0.3)
    ds.m_CopperEdgeClearance = mm(0.2)
    ds.m_HoleToHoleMin = mm(0.25)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(mm(0.15))
    nc.SetTrackWidth(mm(0.2))
    nc.SetViaDiameter(mm(0.6))
    nc.SetViaDrill(mm(0.3))
    nets = {}
    for n in net["nets"]:
        ni = pcbnew.NETINFO_ITEM(board, n)
        board.Add(ni)
        nets[n] = ni
    for ref, part in net["parts"].items():
        fp = load_fp(part["fp"])
        fp.SetReference(ref)
        fp.SetValue(part["value"])
        board.Add(fp)
        x, y, rot, side = placement[ref]
        if mirror_x:
            x = w - x
            rot = (180 - rot) % 360 if rot in (90, 270) else rot
        fp.SetPosition(vec(x, y))
        if side == "B":
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetOrientationDegrees(rot)
        bb = fp.GetBoundingBox(False)
        c = bb.GetCenter()
        fp.Move(pcbnew.VECTOR2I(mm(x) - c.x, mm(y) - c.y))
        for pad in fp.Pads():
            n = pin_net.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(nets[n])
    for i, (x, y) in enumerate(holes, 1):
        fp = load_fp("MountingHole:MountingHole_2.2mm_M2_Pad")
        fp.SetReference(f"H{i}")
        board.Add(fp)
        fp.SetPosition(vec(x, y))
    outline(board, w, h)
    for k in [(0, 0, w, 0.35), (0, h - 0.35, w, h), (0, 0, 0.35, h), (w - 0.35, 0, w, h)]:
        add_keepout(board, *k)   # perimeter ring: the router keeps tracks and vias off the board edge
    for k in keepouts:
        add_keepout(board, *k)
    gnd = nets.get("GND")
    if gnd is not None:
        for layer in ([pcbnew.F_Cu, pcbnew.B_Cu] if layers == 2 else [pcbnew.In1_Cu, pcbnew.In2_Cu]):
            add_zone(board, layer, gnd, w, h)
    out = d / f"{variant}.kicad_pcb"
    write_project(out.with_suffix(".kicad_pro"))
    board.Save(str(out))
    return board, out


def write_project(path):
    """Design rules and DRC severities, so kicad-cli applies the same limits as the router."""
    pro = {
        "meta": {"filename": path.name, "version": 3},
        "board": {"design_settings": {
            "rules": {"min_clearance": 0.15, "min_track_width": 0.15, "min_via_diameter": 0.6,
                      "min_through_hole_diameter": 0.3, "min_copper_edge_clearance": 0.2,
                      "min_hole_to_hole": 0.25, "min_via_annular_width": 0.13, "min_silk_clearance": 0.0},
            "rule_severities": {"silk_over_copper": "ignore", "silk_overlap": "ignore",
                                "silk_edge_clearance": "ignore", "lib_footprint_issues": "ignore",
                                "lib_footprint_mismatch": "ignore"}}},
        "net_settings": {"classes": [{"name": "Default", "clearance": 0.15, "track_width": 0.2,
                                      "via_diameter": 0.6, "via_drill": 0.3, "wire_width": 6,
                                      "bus_width": 12, "line_style": 0, "microvia_diameter": 0.3,
                                      "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
                                      "diff_pair_via_gap": 0.25, "pcb_color": "rgba(0, 0, 0, 0.000)",
                                      "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647}],
                         "meta": {"version": 4}, "net_colors": None, "netclass_assignments": None,
                         "netclass_patterns": []},
    }
    path.write_text(json.dumps(pro, indent=2), encoding="utf-8")


def route(board, pcb_path):
    dsn = pcb_path.with_suffix(".dsn")
    ses = pcb_path.with_suffix(".ses")
    ses.unlink(missing_ok=True)
    pcbnew.ExportSpecctraDSN(board, str(dsn))
    cmd = [str(JAVA), "-Xmx8g", "-jar", str(FREEROUTING), "-de", str(dsn), "-do", str(ses), "-mp", os.environ.get("ROUTE_PASSES", "12")]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1500)
    log = (r.stdout + r.stderr)[-1500:]
    (pcb_path.with_suffix(".route.log")).write_text(r.stdout + r.stderr, encoding="utf-8")
    if not ses.exists():
        print("freerouting produced no session file:\n", log)
        return False
    pcbnew.ImportSpecctraSES(board, str(ses))
    return True


def finish(board, pcb_path):
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(str(pcb_path))


if __name__ == "__main__":
    which = sys.argv[1]
    import layouts
    board, path = layouts.make(which, build)
    ok = route(board, path)
    finish(board, path)
    print("routed" if ok else "NOT routed", path)
